from django.db import models
from orakel.models.utils import BaseModel

class Operator(BaseModel):
    """An operator is responsible for executing a process step. Depending on the degree of automation, the operator is responsible for setting parameters 
    and recording sensor readings.

    Relationships:
        ProcessStep to Operator: ManyToOne
        Event to Operator: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
