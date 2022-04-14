from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import MachineSerializer
from orakel.models import Machine


class MachineViewSet(CustomModelViewSet):
    """Viewset for Model Machine.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        Machine to ShopFloor: ManyToOne
        ProcessStep to Machine: ManyToOne
        RealSensor to Machine: ManyToOne
        Tool to Machine: ManyToOne 
        Event to Machine: ManyToOne
    """
    serializer_class = MachineSerializer
    django_model = Machine
