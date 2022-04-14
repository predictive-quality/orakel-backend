from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from orakel.serializers.v1 import SensorSerializer
from rest_framework import serializers

class MachineLearningRunSerializer(BaseSerializer):
    """Execution of a MachineLearningRunSpecification with parameter values.
    Relationships:
        MachineLearningRun to MachineLearningRunSpecification: ManyToOne
        ProcessStepSpecification to MachineLearningRun: OneToOne
    """
    url = HyperlinkedIdentityField(view_name="machinelearningrun-detail", read_only=True)
    machinelearningrunspecification = PrimaryKeyRelatedField(view_name='machinelearningrunspecification-detail',read_only=False, many=False, required=False, queryset=models.MachineLearningRunSpecification.objects.all(), style={'base_template': 'input.html'})
    sensor = PrimaryKeyRelatedField(view_name="sensor-detail", read_only=False, many=True, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    processstepspecification = PrimaryKeyRelatedField(view_name="processstepspecification-detail", read_only=False, many=False, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})

    argo_job_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    parameter = serializers.JSONField(read_only=True)
    save_path = serializers.CharField(read_only=True)
    results = serializers.CharField(read_only=True)
    deployed  = serializers.BooleanField(read_only=True)
    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    exclude_many_relations_from_filter_url = ()  

    class Meta:
        model = models.MachineLearningRun
        fields = ('id', 'url', 'name', 'description', 'status', 'sensor', 'save_path', 'deployed', 'inference', 'parameter', 'results', 'processstepspecification', 'machinelearningrunspecification', 'argo_job_id')
        depth = 1
