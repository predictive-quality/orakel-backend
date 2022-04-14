from django.db import models
from orakel.models.utils import BaseModel


class PipelineBlock(BaseModel):
    """The PipelineBlockSpecification is the parent instance of the PipelineBlock. 
    The PipelineBlock should have values for it's parents parameters in order to refer to a ml-run-specification so it can executed with a ML-Run.
    Relationships:
        PipelineBlock to MachineLearingRunSpecification: ManyToMany
        PipelineBlock to PipelineBlockSpecification: ManyToOne
    """

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    parameter = models.JSONField(default=None, null=True, blank=True)

    # Related fields
    machinelearningrunspecification = models.ManyToManyField("MachineLearningRunSpecification", related_name="%(class)s", default=None, blank=True)
    pipelineblockspecification = models.ForeignKey('PipelineBlockSpecification', related_name='%(class)s', default=None, blank=True, null=True, on_delete=models.SET_NULL)

