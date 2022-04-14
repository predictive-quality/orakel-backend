# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import SensorSerializer
from orakel import models


class SensorViewSet(CustomModelViewSet):
    """Viewset for Model RealSensor.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        RealSensor to Machine: ManyToOne
        RealSensor to ShopFloor: ManyToOne
        RealSensor to Tool: ManytoOne
        QualityCharacteristics to RealSensor: OneToOne
        ProcessParameter to RealSensor: OneToOne
        SensorReading to Sensor: ManyToOne
        Event to Sensor: ManyToOne
    """
    serializer_class = SensorSerializer
    django_model = models.Sensor
