# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel


class Sensor(BaseModel):
    """A sensor delivers measurements (cmp. Sensor Readings).
    A sensor is measuring a physical quantity or virtual value.

    Relationships:
        SensorReading to Sensor: ManyToOne
        Sensor to Machine: ManyToOne
        Sensor to ShopFloor: ManyToOne
        Sensor to Tool: ManytoOne
        QualityCharacteristics to Sensor: ManyToMany
        ProcessParameter to Sensor: ManyToOne
        Event to Sensor: ManyToOne
        Sensor to MachineLearningRun: ManyToOne
    """

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
    virtual = models.BooleanField(default=False, blank=True, null=True)

    machine = models.ForeignKey('Machine', related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
    shopfloor = models.ForeignKey('ShopFloor', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    tool = models.ForeignKey('Tool', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    machinelearningrun = models.ForeignKey('MachineLearningRun', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
