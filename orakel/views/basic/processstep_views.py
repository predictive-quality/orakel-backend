from orakel.models.basic.processstep import ProcessStep
from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ProcessStepSerializer
from orakel.models import ProcessStep


class ProcessStepViewSet(CustomModelViewSet):
    """Viewset for Model ProcessStep.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        ProcessStep to Machine: ManyToOne
        ProcessStep to Operator: ManyToOne
        ProcessStep to ProcessStepSpecification: ManyToOne
        ProcessStep to Product: ManyToOne
        ProcessStep to PreProduct: ManyToOne
        Tool to ProcessStep: ManyToMany
        SensorReading to ProcessStep: ManyToOne
        Event to ProcessStep: ManyToOne

    """
    serializer_class = ProcessStepSerializer
    django_model = ProcessStep


    def __init__(self, *args, **kwargs):
            super(ProcessStepViewSet, self).__init__(*args, **kwargs)
            self.filter_fields["started"].extend(["gte", "lte"])
            self.filter_fields["ended"].extend(["gte", "lte"])