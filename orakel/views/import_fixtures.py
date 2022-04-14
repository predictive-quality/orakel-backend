# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import serializers, viewsets
from rest_framework import status as rf_status
from orakel_api.settings import DATABASES
from job_scheduler import tasks

class ImportFixturesSerializer(serializers.Serializer):
    """Serializer to make the ImportFixtures ViewSet work
    """
    input_path = serializers.CharField(max_length=500)




class ImportFixturesViewSet(viewsets.ViewSet):
    """The viewset schedules a task that import fixtures from a s3 bucket and loads them into the database where it was requested from.
    Returns a bad request when the database does not exist or one of the fields is none.
    Only post request will be accepted. The get request is only for the Endpoint View.
    Data to supply: {"input_path": directory_path_to_fixtures, }

    Returns:
        [Response]: Http Response
    """
    http_method_names = ['post', 'get']
    permission_classes = [ IsAdminUser ]
    serializer_class = ImportFixturesSerializer

    @staticmethod
    def validate_database(database):
        return True if database in DATABASES.keys() else False

    def list(self, request, database):
            serializer = ImportFixturesSerializer(instance=None, data={"input_path": None})
            serializer.is_valid()
            return Response(serializer.data)

    def post(self, request, database,*args, **kwargs):

        input_path = request.data.get("input_path", None)

        valid_database = self.validate_database(database)
        if database and input_path and valid_database:
            tasks.c_import_fixtures.delay(database=database, input_path=input_path)
            msg = "Task scheduled."
            status = rf_status.HTTP_202_ACCEPTED
        else:
            msg = "{}".format("Input_path is required" if valid_database else "A valid databasename is required!")
            status = rf_status.HTTP_400_BAD_REQUEST


        return Response(status=status, data=msg)
