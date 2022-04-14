from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ToolSerializer
from orakel.models import Tool, Machine, ProcessStep, Sensor, Event


class ToolViewSet(CustomModelViewSet):
    """Viewset for Model Tool.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        Tool to Machine: ManyToOne
        Tool to ProcessStep: ManyToMany
        Sensor to Tool: ManyToOne
        Event to Tool: ManyToOne
    """
    serializer_class = ToolSerializer
    django_model = Tool
