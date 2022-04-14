from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class SensorSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Sensor.

    Model Relationships:
        Sensor to Machine: ManyToOne
        Sensor to ShopFloor: ManyToOne
        Sensor to Tool: ManytoOne
        QualityCharacteristics to RealSensor: OneToOne
        ProcessParameter to RealSensor: OneToOne
        SensorReading to Sensor: ManyToOne
        Event to Sensor: ManyToOne
        Sensor to MachineLearningRun: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="sensor-detail", read_only=True)
    sensorreading = PrimaryKeyRelatedField(view_name='sensorreading-detail',read_only=False, many=True, required=False, queryset=models.SensorReading.objects.all(), style={'base_template': 'input.html'})
    processparameter = PrimaryKeyRelatedField(view_name='processparameter-detail',read_only=False, many=True, required=False, queryset=models.ProcessParameter.objects.all(), style={'base_template': 'input.html'})
    qualitycharacteristics = PrimaryKeyRelatedField(view_name='qualitycharacteristics-detail',read_only=False, many=True, required=False, queryset=models.QualityCharacteristics.objects.all(), style={'base_template': 'input.html'})
    machine = PrimaryKeyRelatedField(view_name='machine-detail',read_only=False, many=False, required=False, queryset=models.Machine.objects.all(), style={'base_template': 'input.html'})
    shopfloor = PrimaryKeyRelatedField(view_name='shopfloor-detail',read_only=False, many=False, required=False, queryset=models.ShopFloor.objects.all(), style={'base_template': 'input.html'})
    tool = PrimaryKeyRelatedField(view_name='tool-detail',read_only=False, many=False, required=False, queryset=models.Tool.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})
    machinelearningrun = PrimaryKeyRelatedField(view_name='machinelearningrun-detail',read_only=False, many=False, required=False, queryset=models.MachineLearningRun.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',) 

    class Meta:
        model = models.Sensor
        fields = ('id','name','url','description','virtual','sensorreading','processparameter','qualitycharacteristics','machine','shopfloor','tool','machinelearningrun', 'event')
        depth = 1

