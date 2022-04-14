from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import EventSerializer
from orakel.models import Event


class EventViewSet(CustomModelViewSet):
    """Viewset for Model Event.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        Event to Machine: ManyToOne
        Event to Operator: ManyToOne
        Event to ProcessParameter: ManyToOne
        Event to ProcessStep: ManyToOne
        Event to ProcessStepSpecification: ManyToOne
        Event to Product: ManyToOne
        Event to PreProduct: ManyToOne
        Event to ProductSpecification: ManyToOne
        Event to QualityCharacteristics: ManyToOne
        Event to RealSensor: ManyToOne
        Event to VirtualSensor: ManyToOne
        Event to SensorReading: ManyToOne
        Event to ShopFloor: ManyToOne
        Event to Tool: ManyToOne
    """
    serializer_class = EventSerializer
    django_model = Event