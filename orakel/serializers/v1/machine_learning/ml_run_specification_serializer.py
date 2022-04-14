# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework import serializers


class MachineLearningRunSpecificationSerializer(BaseSerializer):
    """Machine Learning Run Specification that has ordered PipeLineBlocks and contains a reference to a DataFrame.
    Cunstruct a case with a combination of PipeLineBlocks that use the linked DataFrame.
    The Model pretend the parameters (without values) for the MachineLearningRun.

    Relationships:
        MachineLearningRunSpecification to DataFrame: ManyToOne
        PipelineBlock to MachineLearningRunSpecification: ManyToMany
        MachineLearningRun to MachineLearningRunSpecification: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="machinelearningrunspecification-detail", read_only=True)
    dataframe = PrimaryKeyRelatedField(view_name='dataframe-detail',read_only=False, many=False, required=False, queryset=models.DataFrame.objects.all(), style={'base_template': 'input.html'})
    pipelineblock = PrimaryKeyRelatedField(view_name='pipelineblock-detail',read_only=False, many=True, required=False, queryset=models.PipelineBlock.objects.all(), style={'base_template': 'input.html'})
    machinelearningrun = PrimaryKeyRelatedField(view_name='machinelearningrun-detail',read_only=False, many=True, required=False, queryset=models.MachineLearningRun.objects.all(), style={'base_template': 'input.html'})

    argo_template = serializers.CharField(read_only=True, required=False)

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    exclude_many_relations_from_filter_url = ('pipelineblock',)

    class Meta:
        model = models.MachineLearningRunSpecification
        fields = ('id', 'url', 'name', 'description', 'save_path' ,'pipeline_order','dataframe', 'pipelineblock', 'machinelearningrun', 'argo_template')
        depth = 1
