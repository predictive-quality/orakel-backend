# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class SensorReading(BaseModel):
    """A sensor reading is a recording of a sensor value at a given point in time.

    Relationships:
        SensorReading to Sensor: ManyToOne
        SensorReading to ProcessStep: ManyToOne
        SensorReading to ProcessParameter: ManyToOne
        SensorReading to QualityCharacteristics: ManyToOne
        Event to SensorReading: ManyToOne
    """

    value = models.FloatField(default=None ,null=True, blank=True)
    date = models.DateTimeField(default=None ,null=True, blank=True)

    sensor = models.ForeignKey('Sensor', related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
    processstep = models.ForeignKey('ProcessStep',  related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
    processparameter = models.ForeignKey('ProcessParameter', related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
    qualitycharacteristics = models.ForeignKey('QualityCharacteristics', related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=['processparameter']),
                  models.Index(fields=['qualitycharacteristics']),
                  models.Index(fields=['processstep']),
                  models.Index(fields=['sensor']),
                  ]


    def __str__(self):
        return str(self.pk)
