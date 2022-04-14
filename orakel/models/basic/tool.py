from django.db import models
from orakel.models.utils import BaseModel

class Tool(BaseModel):
    """tool can be mounted on any qualified machine. Smart tools may include sensors of their own.

    Relationships:
        Tool to Machine: ManyToOne
        Tool to ProcessStep: ManyToMany
        Sensor to Tool: ManyToOne
        Event to Tool: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
    machine = models.ForeignKey('Machine', related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
    processstep = models.ManyToManyField('ProcessStep', related_name='%(class)s', default=None ,null=True, blank=True)
