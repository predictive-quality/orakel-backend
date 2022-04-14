# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class SensorReadingSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model SensorReading.

    Relationships:
        SensorReading to Sensor: ManyToOne
        SensorReading to ProcessStep: ManyToOne
        Event to SensorReading: ManyToOne
    """

    url = HyperlinkedIdentityField(view_name="sensorreading-detail", read_only=True)
    sensor = PrimaryKeyRelatedField(view_name='sensor-detail',read_only=False, many=False, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, allow_null=True, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})
    processparameter = PrimaryKeyRelatedField(view_name='processparameter-detail',read_only=False, many=False, required=False, queryset=models.ProcessParameter.objects.all(), style={'base_template': 'input.html'})
    qualitycharacteristics = PrimaryKeyRelatedField(view_name='qualitycharacteristics-detail',read_only=False, many=False,required=False, queryset=models.QualityCharacteristics.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',)

    class Meta:
        model = models.SensorReading
        fields = ('id','url','value','date','sensor', 'processparameter', 'qualitycharacteristics','processstep','event')
        depth = 1
