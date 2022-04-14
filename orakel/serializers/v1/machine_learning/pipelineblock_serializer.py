# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models.machine_learning import pipelineblockspecification
from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework import serializers

class PipelineBlockSerializer(BaseSerializer):
    """The PipelineBlockSpecification is the parent instance of the PipelineBlock.
    The PipelineBlock should have values for it's parents parameters in order to refer to a ml-run-specification so it can executed with a ML-Run.
    Relationships:
        PipelineBlock to MachineLearingRunSpecification: ManyToMany
        PipelineBlock to PipelineBlockSpecification: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="pipelineblock-detail", read_only=True)
    machinelearningrunspecification = PrimaryKeyRelatedField(view_name='machinelearningrunspecification-detail',read_only=False, many=True,  required=False, queryset=models.MachineLearningRunSpecification.objects.all(), style={'base_template': 'input.html'})
    pipelineblockspecification = PrimaryKeyRelatedField(view_name='pipelineblockspecification-detail',read_only=False, many=False, required=False, queryset=models.PipelineBlockSpecification.objects.all(), style={'base_template': 'input.html'})

    parameter = serializers.JSONField(required=False, allow_null=True)
    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    exclude_many_relations_from_filter_url = ()

    class Meta:
        model = models.PipelineBlock
        fields = ('id', 'url', 'name', 'description', 'parameter', 'machinelearningrunspecification', 'pipelineblockspecification')
        depth = 1


    def validate_parameter(self, value):
        """Check if the related PipelineSpecification has the keys of the parameter dictionary.

        Args:
            value (dict): parameter field value

        Raises:
            serializers.ValidationError: Error message

        Returns:
            [dict]: parameter field value
        """

        error_msg = None
        error = False

        if 'pipelineblockspecification' in self.initial_data:
            pipespec_id = self.initial_data['pipelineblockspecification']
        elif hasattr(self, 'instance'):
            if hasattr(self.instance,  "pipelineblockspecification_id"):
                print(vars(self.instance))
                pipespec_id = self.instance.pipelineblockspecification_id
            else:
                pipespec_id = None
        else:
            pipespec_id = None

        if pipespec_id:
            if models.PipelineBlockSpecification.objects.filter(pk=pipespec_id).exists():
                specification_parameter = list(models.PipelineBlockSpecification.objects.filter(pk=pipespec_id).values_list('parameter', flat=True))[0]
                for key in value.keys():
                    if not key in specification_parameter:
                        error = True
                        error_msg = "Parameter {} was not found in the PipelineBlockSpecification.parameter with pk {}!".format(key, pipespec_id)
                        break
            else:
                error = True
                error_msg = "Related PipelineBlockSpecification with pk {} does not exist!".format(pipespec_id)
        else:
            error = True
            error_msg = "Please link a PipelineBlockSpecification before updating parameter!"

        if error:
            raise serializers.ValidationError(error_msg)

        return value
