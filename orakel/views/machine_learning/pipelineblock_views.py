from rest_framework.response import Response
from rest_framework import status as rf_status

from orakel.models.machine_learning.pipelineblockspecification import PipelineBlockSpecification
from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import PipelineBlockSerializer
from orakel import models, views


class PipeLineBlockViewSet(CustomModelViewSet):
    """The PipelineBlockSpecification is the parent instance of the PipelineBlock. 
    The PipelineBlock should have values for it's parents parameters in order to refer to a ml-run-specification so it can executed with a ML-Run.
    Relationships:
        PipelineBlock to MachineLearingRunSpecification: ManyToMany
        PipelineBlock to PipelineBlockSpecification: ManyToOne
    """

    serializer_class = PipelineBlockSerializer
    django_model = models.PipelineBlock
    
    def __init__(self, *args, **kwargs):
        super(PipeLineBlockViewSet, self).__init__(*args, **kwargs)
        del self.filter_fields["parameter"] # Remove JsonField from filter fields.There is no filter method fpr JsonFields yet.

    

