# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class ProcessStepSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model ProcessStep.

    Relationships:
        ProcessStep to Machine: ManyToOne
        ProcessStep to Operator: ManyToOne
        ProcessStep to ProcessStepSpecification: ManyToOne
        ProcessStep to Product: ManyToOme
        ProcessStep to PreProduct: ManyToOne
        Tool to ProcessStep: ManyToMany
        SensorReading to ProcessStep: ManyToOne
        Event to ProcessStep: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="processstep-detail", read_only=True)
    machine = PrimaryKeyRelatedField(view_name='machine-detail',read_only=False, many=False, required=False, queryset=models.Machine.objects.all(), style={'base_template': 'input.html'})
    operator = PrimaryKeyRelatedField(view_name='operator-detail',read_only=False, many=False,  required=False, queryset=models.Operator.objects.all(), style={'base_template': 'input.html'})
    processstepspecification = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=False,required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})
    product = PrimaryKeyRelatedField(view_name='product-detail',read_only=False, many=False, required=False, queryset=models.Product.objects.all(), style={'base_template': 'input.html'})
    preproduct = PrimaryKeyRelatedField(view_name='preproduct-detail',read_only=False, many=False,  required=False, queryset=models.PreProduct.objects.all(), style={'base_template': 'input.html'})
    tool = PrimaryKeyRelatedField(view_name='tool-detail',read_only=False, many=True,  required=False, queryset=models.Tool.objects.all(), style={'base_template': 'input.html'})
    sensorreading = PrimaryKeyRelatedField(view_name='sensorreading-detail',read_only=False, many=True, required=False, queryset=models.SensorReading.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',)


    class Meta:
        model = models.ProcessStep
        fields = ('id','url','name','status','started','ended','machine','operator','processstepspecification','product','preproduct','tool','sensorreading','event')
        depth = 1
