# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models.basic import productspecification
from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import DataFrameSerializer
from orakel import models

from job_scheduler import tasks

from rest_framework.decorators import action
from rest_framework import status as rf_status
from rest_framework.response import Response

from django.db.models import Q


class DataFrameViewSet(CustomModelViewSet):
    """A model that creates a DataFrame from sensorreadings for a ML-Run.
    A pandas DataFrame will be created after selecting related models in the following order.
    Productspecification --> ProcesStepSpecification --> ProcessParameter / QualityCharacteristic
    When a DataFrame was built, there will be saved a features.fth and target.fth file at the save_path

    Viewset extra Actions:
        create_dataframe: Queue a job in the scheduler

    Relationships:
        Dataframe to ProductSpecification: ManyToOne
        Dataframe to ProcessStepSpecification: ManyToMany
        Dataframe to ProcessParameter: ManyToMany
        Dataframe to QualityCharacteristics: ManyToMany
        Dataframe to target_value(QualityCharacteristics): ManyToMany
        MachineLearningRunSpecification to DataFrame: ManyToOne
    """

    serializer_class = DataFrameSerializer
    django_model = models.DataFrame

    def __init__(self, *args, **kwargs):
        super(DataFrameViewSet, self).__init__(*args, **kwargs)
        del self.filter_fields["feature_config"] # Remove JsonField from filter fields.There is no filter method fpr JsonFields yet.


    @action(detail=True, methods=["get"])  # Detail=True to use action/method on an instance.
    def create_dataframe(self, request, pk, database):
        """Submits the celery task CreateDataframe.
        """

        # Check if nessesary field values are given.

        if self.django_model.objects.filter(Q(pk=pk) & Q(productspecification__isnull=True)).exists():
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="DataFrame instance has no related productspecification!")

        if self.django_model.objects.filter(Q(pk=pk) & Q(processstepspecification__isnull=True)).exists():
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="DataFrame instance has no related processstepspecification!")

        if self.django_model.objects.filter(Q(pk=pk) & Q(processparameter__isnull=True) & Q(qualitycharacteristics__isnull=True)).exists():
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="DataFrame instance has no related processparameter or qualitycharacteristics!")

        if self.django_model.objects.filter(Q(pk=pk) & Q(target_value__isnull=True)).exists():
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="DataFrame instance has no related target_value!")

        if self.django_model.objects.filter(Q(pk=pk) & Q(save_path__isnull=True)).exists():
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="DataFrame instance has no save_path!")

        methods_per_feature = self.django_model.objects.filter(pk=pk).values('feature_config')[0].get('feature_config')

        if len(methods_per_feature) == 0:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Please provide a Method for the feature processparameter/qualitycharacteristics!")

        # Restricts the amount of columns to 500
        features_pp = self.django_model.objects.filter(pk=pk).values_list('processparameter', flat=True).count()
        features_qc = self.django_model.objects.filter(pk=pk).values_list('qualitycharacteristics', flat=True).count()

        if len(methods_per_feature) * (features_pp + features_qc) > 1000:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="To many features supplied (max of 500). amount_feautres = (amount_processparameter + amount_qualitycharacteristics) * amount_methods")

        # Update job status to scheduled.
        self.django_model.objects.filter(pk=pk).update(**{"status": "Scheduled"})

        # Submit task to the queue and worker pods.
        tasks.CreateDataframe().delay(pk=pk, database_name=database, methods_per_feature=methods_per_feature, product_ids=None)

        return Response(status=rf_status.HTTP_200_OK, data="Job create_dataframe was submitted!")
