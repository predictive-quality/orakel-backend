# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from django.core.validators import int_list_validator
from orakel.models.utils import BaseModel
from django_mysql.models import ListTextField


class DataFrame(BaseModel):
    """A model that creates a DataFrame from sensorreadings for a ML-Run.
    A pandas DataFrame will be created after selecting related models in the following order.
    Productspecification --> ProcesStepSpecification --> ProcessParameter and QualityCharacteristics
    When a DataFrame was built, there will be saved a features.fth and target.fth file at the save_path

    Relationships:
        Dataframe to ProductSpecification: ManyToOne
        Dataframe to ProcessStepSpecification: ManyToMany
        Dataframe to ProcessParameter: ManyToMany
        Dataframe to QualityCharacteristics: ManyToMany
        Dataframe to target_value(QualityCharacteristics): ManyToMany
        MachineLearningRunSpecification to DataFrame: ManyToOne
    """
    status_choices = ( ('Pending', 'Pending'),
                        ('Scheduled', 'Scheduled'),
                        ('Failed', 'Failed'),
                        ('Succeeded', 'Succeeded'),
                        ('Running', 'Running'),
                        ('Other', 'Other')
    )


    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
    status = models.CharField(default='Other', choices=status_choices, max_length=20)
    save_path = models.CharField(max_length=200, blank=True, null=True, default=None)
    product_amount = models.PositiveIntegerField(default=500000)
    time_series_data = models.BooleanField(default=False, blank=True, null=True)
    random_records = models.BooleanField(default=True, blank=True, null=True)
    feature_config = models.JSONField(default=None, null=True, blank=True)

    # Related Fields
    productspecification = models.ForeignKey('ProductSpecification', related_name='%(class)s', default=None, blank=True, null=True, on_delete=models.SET_NULL)
    processstepspecification = models.ManyToManyField('ProcessStepSpecification', related_name='%(class)s', default=None, blank=True)
    processparameter = models.ManyToManyField('ProcessParameter', related_name='%(class)s', default=None, blank=True)
    qualitycharacteristics = models.ManyToManyField('QualityCharacteristics', related_name='%(class)s', default=None, blank=True)
    target_value = models.ManyToManyField('QualityCharacteristics', related_name='target_value', default=None, blank=True)
