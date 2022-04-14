# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models.basic.productspecification import ProductSpecification
from django.db import models
from orakel.models.utils import BaseModel

class ProcessStepSpecification(BaseModel):
    """The process step specification contains the reference parameters and the expected ranges for sensor readings.
    It is linked to all its Process Step instances, where the effective parameters are stored.

    Relationships:
        ProcessStep to ProcessStepSpecification: ManyToOne
        ProcessParameter to ProcessStepSpecification: ManyToOne
        Event to ProcessStepSpecification: ManyToOne
        ProcessStepSpecification to Productspecification: ManyToOne
        ProcessStepSpecification to MachineLearningRun: OneToOne

    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
    optional = models.BooleanField(default=None ,null=True, blank=True)
    previous_pss = models.ManyToManyField('ProcessStepSpecification', related_name='previous', default=None, blank=True )
    next_pss = models.ManyToManyField('ProcessStepSpecification', related_name='next', default=None, blank=True)

    productspecification = models.ForeignKey('ProductSpecification',  related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL)
    machinelearningrun = models.OneToOneField("MachineLearningRun", related_name="%(class)s", default=None, blank=True, null=True, on_delete=models.SET_NULL)

    def add_previous_pss(self, previous_pss):
        self.previous_pss.add(previous_pss)

    def remove_previous_pss(self, previous_pss):
        self.previous_pss.remove(previous_pss)

    def add_next_pss(self, next_pss):
        self.next_pss.add(next_pss)

    def remove_next_pss(self, next_pss):
        self.next_pss.remove(next_pss)
