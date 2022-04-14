# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import MachineLearningRunSerializer, SensorSerializer, ProcessStepSpecificationSerializer
from orakel import models

from rest_framework.response import Response
from rest_framework import status as rf_status
from rest_framework.decorators import action

from Argo.utils import ArgoRequest
import json

class MachineLearningRunViewSet(CustomModelViewSet):
    """Execution of a MachineLearningRunSpecification with parameter values.
    Relationships:
        MachineLearningRun to MachineLearningRunSpecification: ManyToOne
        ProcessStepSpecification to MachineLearningRun: OneToOne
    """
    serializer_class = MachineLearningRunSerializer
    django_model = models.MachineLearningRun


    def __init__(self, *args, **kwargs):
        super(MachineLearningRunViewSet, self).__init__(*args, **kwargs)
        del self.filter_fields["parameter"] # Remove JsonField from filter fields.There is no filter method fpr JsonFields yet.
        del self.filter_fields["results"] # Remove JsonField from filter fields.There is no filter method fpr JsonFields yet.


    @action(detail=True, methods=['get']) # Detail=True to use action/method on an instance.
    def terminate(self, requests, pk, *args, **kwargs):
        """Terminate an argo workflow when it is running.
        Args:
            pk (int): id of the machinelearningrun instance

        Returns:
            [Response]: status code and reason from the request to argo.
        """


        job_status_to_terminate = ["Running", "Pending", "Scheduled"]
        mlrun = list(models.MachineLearningRun.objects.filter(pk=pk).values_list('status', 'argo_job_id'))[0]
        # Only send terminate request when the status is in job_status_to_terminate
        if mlrun[0] in job_status_to_terminate:
            argo_request = ArgoRequest()
            url = argo_request.url_workflow_put.rstrip("/") + "/" + mlrun[1] + "/terminate"
            res = argo_request.make_request("PUT", url=url, data=None, max_wait=0, step=1)
            return Response(status=res.status_code, data=res.reason)
        else:
            return Response(status=rf_status.HTTP_409_CONFLICT, data="MachineLearningRun with status {} does not seem to run!".format(mlrun[0]))


    def create_related_objects(self, pk: int):
        """Create virtual sensors for the target values of the dataframe that is linked to the machinelearningrunspecification.

        Args:
            pk (int): Id of the MachineLearningRun instance.

        Raises:
            ValueError: Dataframe instance has no target_values!
            ValueError: MachineLearningRunSpecification instance has no Dataframe instance
            ValueError: MachineLeariningRun instance has no MachineLearingRunSpecification instance
        """
        try:
            mlrun = models.MachineLearningRun.objects.get(pk=pk)
        except models.MachineLearningRun.DoesNotExist:
            raise "MachineLearningRun with pk does not exists!".format(pk)

        # Get the qualitycharacteristics to create a sensor for
        if hasattr(mlrun, "machinelearningrunspecification"):
            mlrun_spec = mlrun.machinelearningrunspecification
            if hasattr(mlrun_spec, "dataframe"):
                mlrun_spec_df = mlrun_spec.dataframe
                if hasattr(mlrun_spec_df, "target_value") and hasattr(mlrun_spec_df, "productspecification"):
                    target_values = models.DataFrame.objects.get(pk=mlrun_spec_df.pk).target_value.all()
                    productspecification = mlrun_spec_df.productspecification
                else:
                    raise ValueError("Dataframe instance has no target_values or productspecification!")
            else:
                raise ValueError("MachineLearningRunSpecification instance has no Dataframe instance!")
        else:
            raise ValueError("MachineLeariningRun instance has no MachineLearingRunSpecification instance!")

        # create sensor data
        sensor_data = []
        for tv in target_values:
            data = {"name": "{}_{}_{}".format(mlrun.name, mlrun_spec_df.name, tv.name),
                    "virtual": True,
                    "description": "Prediction Sensor for run {} and target_value {} of dataframe {}.".format(mlrun.name, tv.name, mlrun_spec_df.name),
                    "qualitycharacteristics": [tv.pk],
                    "machinelearningrun": pk}
            sensor_data.append(data)

        # create productspecificatipn
        processstepspecification_data = {
            "name": "{}-{}-{}".format(mlrun.name, productspecification.name, "Prediction"),
            "optional": True,
            "productspecification": productspecification.pk,
            "machinelearningrun": pk
        }

        processstepspecification_serializer = ProcessStepSpecificationSerializer(data=processstepspecification_data, many=False, context=self.get_serializer_context())
        if processstepspecification_serializer.is_valid(raise_exception=True):
            processstepspecification_serializer.save()
        else:
            return processstepspecification_serializer

        # create sensor
        sensor_serializer = SensorSerializer(data=sensor_data, many=True, context=self.get_serializer_context())
        if sensor_serializer.is_valid(raise_exception=True):
            sensor_serializer.save()

        return sensor_serializer

    @action(detail=True, methods=['get'])
    def deploy(self, requests, pk, *args, **kwargs):
        """Deploy the run to the inference. It automatically create the nessesary virtual sensor instances.

        Args:
            pk (int): Id of the MachineLearningRun instance.
        """
        mlrun = models.MachineLearningRun.objects.get(pk=pk)

        if mlrun.deployed == True:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="The run is already deployed! Undeploy first and try to deploy again.")

        if mlrun.status != "Succeeded":
            return Response(status=rf_status.HTTP_424_FAILED_DEPENDENCY, data="The run must have been completed successfully to deploy it! Status is {}".format(mlrun[0]))

        # Create virtual sensor for predictions
        serializer = self.create_related_objects(pk)

        if hasattr(serializer, "error"):
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data=serializer.error)

        # deploy model to seldon core

        mlrun.deployed = True
        mlrun.save()

        return Response(status=rf_status.HTTP_201_CREATED, data=serializer.data)


    def perform_undeploy(self, pk: int):
        """Undeploy the model from Seldon Core and delete related virtual Sensors

        Args:
            pk (int): Id of the MachineLearningRun instance.
        """
        # Delete sensors
        sensor_ids = models.Sensor.objects.filter(machinelearningrun=pk).values_list('id', flat=True)
        models.SensorReading.objects.filter(sensor__in=sensor_ids).delete()
        models.Sensor.objects.filter(pk__in=sensor_ids).delete()
        models.ProcessStepSpecification.objects.filter(machinelearningrun=pk).delete()


    @action(detail=True, methods=['get'])
    def undeploy(self, requests, pk, *args, **kwargs):
        """Undeploy the model from Seldon Core and delete related virtual Sensors

        Args:
            pk (int): Id of the MachineLearningRun instance
        """
        # Perform undeploy
        self.perform_undeploy(pk=pk)
        mlrun = models.MachineLearningRun.objects.get(pk=pk)
        mlrun.deployed = False
        mlrun.save()


        return Response(status=rf_status.HTTP_200_OK, data="Undeployed!")


    def destroy(self, request, *args, **kwargs):
        """Override destory method to perform undeploy before deletion.
        """
        instance = self.get_object()
        # Perform undeploy before deleting the instance
        self.undeploy(instance.pk)
        self.perform_destroy(instance)
        return Response(status=rf_status.HTTP_204_NO_CONTENT)
