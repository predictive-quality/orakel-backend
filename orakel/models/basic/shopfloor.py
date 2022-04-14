# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class ShopFloor(BaseModel):
    """A shop floor usually contains multiple machines and can be, for example, equipped with environmental sensors.

    Relationships:
        Machine to ShopFloor: ManyToOne
        Sensor to ShopFloor: ManyToOne
        Event to ShopFloor: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
