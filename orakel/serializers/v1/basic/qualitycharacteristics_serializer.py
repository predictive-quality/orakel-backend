from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class QualityCharacteristicsSerializer(BaseSerializer):
    """HyperLinkedSerializer for Model QualityCharacteristics.

    Relationships:
        QualityCharacteristics to ProcessStepSpecification: ManyToOne
        QualityCharacteristics to Sensor: ManyToMany
        SensorReading to QualityCharacteristics: ManyToOne
        Dataframe to QualityCharacteristics: ManyToMany
        Dataframe to target_value(QualityCharacteristics): ManyToMany
        Event to QualityCharacteristics: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="qualitycharacteristics-detail", read_only=True)
    processstepspecification = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=False, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})
    sensor = PrimaryKeyRelatedField(view_name='sensor-detail',read_only=False, many=True, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})
    sensorreading = PrimaryKeyRelatedField(view_name='sensorreading-detail',read_only=False, many=True, required=False, queryset=models.SensorReading.objects.all(), style={'base_template': 'input.html'})
    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',) 

    class Meta:
        model = models.QualityCharacteristics
        fields = ('id','url','name','description','targetvalue','hardupperlimit','hardlowerlimit','softupperlimit','softlowerlimit','unit','processstepspecification','sensor','sensorreading', 'event')
        depth  = 1