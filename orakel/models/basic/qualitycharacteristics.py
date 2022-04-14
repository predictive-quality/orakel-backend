# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class QualityCharacteristics(BaseModel):
    """QualityCharateristics deliver features and limits for the sensor and productspecifications.

    Relationships:
        QualityCharacteristics to ProcessStepSpecification: ManyToOne
        QualityCharacteristics to Sensor: ManyToMany
        SensorReading to QualityCharacteristics: ManyToOne
        Dataframe to QualityCharacteristics: ManyToMany
        Dataframe to target_value(QualityCharacteristics): ManyToMany
        Event to QualityCharacteristics: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)

    targetvalue = models.FloatField(default=None, null=True, blank=True)
    hardupperlimit = models.FloatField(default=None, null=True, blank=True)
    hardlowerlimit = models.FloatField(default=None, null=True, blank=True)
    softupperlimit = models.FloatField(default=None, null=True, blank=True)
    softlowerlimit = models.FloatField(default=None, null=True, blank=True)
    unit = models.CharField(max_length=100, default=None, null=True, blank=True)

    processstepspecification = models.ForeignKey('ProcessStepSpecification', related_name='%(class)s',  default=None,null=True, blank=True, on_delete=models.SET_NULL)
    sensor = models.ManyToManyField('Sensor', related_name='%(class)s', default=None, blank=True)


    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=['processstepspecification']),

        ]
