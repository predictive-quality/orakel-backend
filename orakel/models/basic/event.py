# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class Event(BaseModel):
    """An event is an occurrence that can be created by or assigned to all objects.

    Relationships:
        Event to Machine: ManyToOne
        Event to Operator: ManyToOne
        Event to ProcessParameter: ManyToOne
        Event to ProcessStep: ManyToOne
        Event to ProcessStepSpecification: ManyToOne
        Event to Product: ManyToOne
        Event to PreProduct: ManyToOne
        Event to ProductSpecification: ManyToOne
        Event to QualityCharacteristics: ManyToOne
        Event to Sensor: ManyToOne
        Event to SensorReading: ManyToOne
        Event to ShopFloor: ManyToOne
        Event to Tool: ManyToOne
    """

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
    date = models.DateTimeField(default=None, null=True, blank=True)

    machine = models.ForeignKey('Machine', related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
    operator = models.ForeignKey('Operator', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    processparameter = models.ForeignKey('ProcessParameter', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    processstep = models.ForeignKey('ProcessStep', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    processstepspecification = models.ForeignKey('ProcessStepSpecification', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey('Product', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    preproduct = models.ForeignKey('PreProduct', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    productspecification = models.ForeignKey('ProductSpecification', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    qualitycharacteristics = models.ForeignKey('QualityCharacteristics', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    sensor = models.ForeignKey('Sensor', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    sensorreading = models.ForeignKey('SensorReading', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    shopfloor = models.ForeignKey('ShopFloor', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    tool = models.ForeignKey('Tool', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)
