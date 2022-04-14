from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework import serializers

class PipelineBlockSpecificationSerializer(BaseSerializer):
    """PipelineBlockSpecification that defines a Machine Learning Model or further Pipeline blocks in order to create PipeLineBlocks that include values for the parameter.
    Relationships:
        PipelineBlock to PipeLineBlockSpecifcation: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="pipelineblockspecification-detail", read_only=True)
    pipelineblock = PrimaryKeyRelatedField(view_name='pipelineblock-detail',read_only=False, many=True, required=False, queryset=models.PipelineBlock.objects.all(), style={'base_template': 'input.html'})

    parameter = serializers.JSONField(read_only=True, required=False)
    argo_template = serializers.CharField(read_only=True, required=False)
    argo_template_entrypoint = serializers.CharField(read_only=True, required=False)


    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    exclude_many_relations_from_filter_url = () 

    class Meta:
        model = models.PipelineBlockSpecification
        fields = ('id', 'url', 'name', 'description', 'parameter', 'argo_template', 'argo_template_entrypoint', 'pipelineblock')
        depth = 1
