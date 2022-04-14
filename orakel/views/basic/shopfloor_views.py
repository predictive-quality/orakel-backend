# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ShopFloorSerializer
from orakel.models import ShopFloor, Machine, Sensor, Event


class ShopFloorViewSet(CustomModelViewSet):
    """Viewset for Model ShopFloor.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        Machine to ShopFloor: ManyToOne
        Sensor to ShopFloor: ManyToOne
        Event to ShopFloor: ManyToOne:
    """
    serializer_class = ShopFloorSerializer
    django_model = ShopFloor
