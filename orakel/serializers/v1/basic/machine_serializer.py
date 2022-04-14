# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from orakel import models

class MachineSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Machine

    Relationships:
        Machine to ShopFloor: ManyToOne
        ProcessStep to Machine: ManyToOne
        Sensor to Machine: ManyToOne
        Tool to Machine: ManyToOne
        Event to Machine: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="machine-detail", read_only=True)
    sensor = PrimaryKeyRelatedField(view_name='sensor-detail',read_only=False, many=True, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    shopfloor = PrimaryKeyRelatedField(view_name='shopfloor-detail',read_only=False, many=False, required=False, queryset=models.ShopFloor.objects.all(), style={'base_template': 'input.html'})
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, many=True,  required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    tool = PrimaryKeyRelatedField(view_name='tool-detail',read_only=False, many=True, required=False, queryset=models.Tool.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})
    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',)

    class Meta:
        model = models.Machine
        fields = ('id','url','name','description','machinetype','sensor','processstep','shopfloor','tool','event')
        depth  = 1
