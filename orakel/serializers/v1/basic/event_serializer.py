# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField


class EventSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Event.

    Relationships:
        Event to Machine: ManyToOne
        Event to Operator: ManyToOne
        Event to ProcessStep: ManyToOne
        Event to ProcessStepSpecification: ManyToOne
        Event to Product: ManyToOne
        Event to PreProduct: ManyToOne
        Event to ProductSpecification: ManyToOne
        Event to Sensor: ManyToOne
        Event to SensorReading: ManyToOne
        Event to ShopFloor: ManyToOne
        Event to Tool: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="event-detail", read_only=True)
    machine = PrimaryKeyRelatedField(view_name='machine-detail',read_only=False, many=False, required=False, queryset=models.Machine.objects.all(), style={'base_template': 'input.html'})
    operator = PrimaryKeyRelatedField(view_name='operator-detail',read_only=False, many=False, required=False, queryset=models.Operator.objects.all(), style={'base_template': 'input.html'})
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, many=False, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    processstepspecification = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=False, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})
    product = PrimaryKeyRelatedField(view_name='product-detail',read_only=False, many=False, required=False, queryset=models.Product.objects.all(), style={'base_template': 'input.html'})
    preproduct = PrimaryKeyRelatedField(view_name='preproduct-detail',read_only=False, many=False, required=False, queryset=models.PreProduct.objects.all(), style={'base_template': 'input.html'})
    productspecification= PrimaryKeyRelatedField(view_name='productspecification-detail',read_only=False, many=False, required=False, queryset=models.ProductSpecification.objects.all(), style={'base_template': 'input.html'})
    sensor = PrimaryKeyRelatedField(view_name='sensor-detail',read_only=False, many=False, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    sensorreading = PrimaryKeyRelatedField(view_name='sensorreading-detail',read_only=False, many=False, required=False, queryset=models.SensorReading.objects.all(), style={'base_template': 'input.html'})
    shopfloor = PrimaryKeyRelatedField(view_name='shopfloor-detail',read_only=False, many=False, required=False, queryset=models.ShopFloor.objects.all(), style={'base_template': 'input.html'})
    tool = PrimaryKeyRelatedField(view_name='tool-detail',read_only=False, many=False, required=False, queryset=models.Tool.objects.all(), style={'base_template': 'input.html'})
    qualitycharacteristics = PrimaryKeyRelatedField(view_name='qualitycharacteristics-detail',read_only=False, many=False, required=False, queryset=models.QualityCharacteristics.objects.all(), style={'base_template': 'input.html'})
    processparameter = PrimaryKeyRelatedField(view_name='processparameter-detail',read_only=False, many=False, required=False, queryset=models.ProcessParameter.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ()

    class Meta:
        model = models.Event
        fields = ('id','url','name','description','date',
                    'machine',
                    'operator',
                    'processstep',
                    'processstepspecification',
                    'product',
                    'preproduct',
                    'productspecification',
                    'sensor',
                    'sensorreading',
                    'shopfloor',
                    'tool',
                    'qualitycharacteristics',
                    'processparameter'
                    )
