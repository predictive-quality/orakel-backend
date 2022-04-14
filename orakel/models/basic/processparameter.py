# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class ProcessParameter(BaseModel):
    """ProcessParameter specify sensor and processstepspecification characteristics and limits.

    Relationships:
        ProcessParameter to ProcessStepSpecification: ManyToOne
        ProcessParameter to Sensor: ManyToOne
        SensorReading to ProcessParameter: ManyToOne
        Event to ProcessParameter: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)

    targetvalue = models.FloatField(default=None, null=True, blank=True)
    hardupperlimit = models.FloatField(default=None, null=True, blank=True)
    hardlowerlimit = models.FloatField(default=None, null=True, blank=True)
    softupperlimit = models.FloatField(default=None, null=True, blank=True)
    softlowerlimit = models.FloatField(default=None, null=True, blank=True)
    unit = models.CharField(max_length=100, default=None, null=True, blank=True)

    processstepspecification = models.ForeignKey('ProcessStepSpecification', related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL)
    sensor = models.ForeignKey('Sensor', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=['processstepspecification']),
                   models.Index(fields=['sensor']),
        ]
