from django.db import models
from orakel.models.utils import BaseModel

class MachineLearningRunSpecification(BaseModel):
    """Machine Learning Run Specification that has ordered PipeLineBlocks and contains a reference to a DataFrame.
    Cunstruct a case with a combination of PipeLineBlocks that use the linked DataFrame.
    The Model pretend the parameters (without values) for the MachineLearningRun.
    
    Relationships:
        MachineLearningRunSpecification to DataFrame: ManyToOne
        PipelineBlock to MachineLearningRunSpecification: ManyToMany
        MachineLearningRun to MachineLearningRunSpecification: ManyToOne
    """


    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
    pipeline_order = models.JSONField(default=None, null=True, blank=True)
    argo_template = models.CharField(max_length=200, default=None, null=True, blank=True)
    save_path = models.CharField(max_length=200, default=None, null=True, blank=True)
    create_new_template = models.BooleanField(default=True, blank=True, null=True)

    # Related fields

    dataframe = models.ForeignKey('DataFrame', related_name='%(class)s', default=None, blank=True, null=True, on_delete=models.SET_NULL)