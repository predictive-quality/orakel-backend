from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import OperatorSerializer
from orakel.models import Operator


class OperatorViewSet(CustomModelViewSet):
    """Viewset for Model Operator.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        ProcessStep to Operator: ManyToOne
        Event to Operator: ManyToOne

    """
    serializer_class = OperatorSerializer
    django_model = Operator