# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class ToolSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Tool.
    Relationships:
        Tool to Machine: ManyToOne
        Tool to ProcessStep: ManyToMany
        RealSensor to Tool: ManyToOne
        Event to Tool: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="tool-detail", read_only=True)
    machine = PrimaryKeyRelatedField(view_name='machine-detail',read_only=False, many=False, required=False, queryset=models.Machine.objects.all(), style={'base_template': 'input.html'})
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, many=True, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    sensor = PrimaryKeyRelatedField(view_name='sensor-detail',read_only=False, many=True, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',)

    class Meta:
        model = models.Tool
        fields = ('id','name','url','description','machine','processstep','sensor','event')
        depth = 1
