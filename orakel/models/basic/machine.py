# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class Machine(BaseModel):
    """A machine is any type of stationary device that is used in the manufacturing process, for example, a CNCmachine or a coordinate measuring machine.
    It contains relevant information, e.g. a service record.

    Relationships:
        Machine to ShopFloor: ManyToOne
        ProcessStep to Machine: ManyToOne
        Sensor to Machine: ManyToOne
        Tool to Machine: ManyToOne
        Event to Machine: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)

    machinetype = models.CharField(max_length=100, default=None, null=True, blank=True)
    shopfloor = models.ForeignKey('ShopFloor', related_name='%(class)s',  default=None,null=True, blank=True, on_delete=models.SET_NULL)
