from django.db import models
from orakel.models.utils import BaseModel


class PipelineBlockSpecification(BaseModel):
    """PipelineBlockSpecification that defines a Machine Learning Model or further Pipeline blocks in order to create PipeLineBlocks that include values for the parameter.
    Relationships:
        PipelineBlock to PipeLineBlockSpecifcation: ManyToOne
    """

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    parameter = models.JSONField(default=None, null=True, blank=True)
    argo_template = models.CharField(max_length=200, default=None, null=True, blank=True)
    argo_template_entrypoint = models.CharField(max_length=200, default=None, null=True, blank=True)

    # Related fields