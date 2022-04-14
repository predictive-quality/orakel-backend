# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class OperatorSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Operator

    Relationships:
        ProcessStep to Operator: ManyToOne
        Event to Operator: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="operator-detail", read_only=True)
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, many=True, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    event= PrimaryKeyRelatedField(view_name='event-detail',read_only=False,  many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',)

    class Meta:
        model = models.Operator
        fields = ('id','url','name','description','processstep','event')
        depth = 1
