# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class ProcessStepSpecificationSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model ProcessStepSpecification.

    Relationships:
        ProcessStep to ProcessStepSpecification: ManyToOne
        ProcessParameter to ProcessStepSpecification: ManyToOne
        QualityCharacteristics to ProcessStepSpecification: ManyToOne
        Event to ProcessStepSpecification: ManyToOne
        ProcessStepSpecification to Productspecification: ManyToOne
        ProcessStepSpecification to MachineLearningRun: OneToOne

    """
    url = HyperlinkedIdentityField(view_name="processstepspecification-detail", read_only=True)
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, many=True, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    processparameter = PrimaryKeyRelatedField(view_name='processparameter-detail',read_only=False, many=True, required=False, queryset=models.ProcessParameter.objects.all(), style={'base_template': 'input.html'})
    qualitycharacteristics = PrimaryKeyRelatedField(view_name='qualitycharacteristics-detail',read_only=False, many=True, required=False, queryset=models.QualityCharacteristics.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True,  required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})
    previous_pss = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=True, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})
    next_pss = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=True, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})
    productspecification = PrimaryKeyRelatedField(view_name='productspecification-detail',read_only=False,  many=False, required=False, queryset=models.ProductSpecification.objects.all(), style={'base_template': 'input.html'})
    machinelearningrun = PrimaryKeyRelatedField(view_name='machinelearningrun-detail', read_only=False, many=False, required=False, queryset=models.MachineLearningRun.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    exclude_many_relations_from_filter_url = ('next_pss', 'previous_pss')

    class Meta:
        model = models.ProcessStepSpecification
        fields = ('id', 'url', 'name', 'description', 'optional','next_pss', 'previous_pss', 'productspecification','processstep', 'processparameter', 'qualitycharacteristics', 'machinelearningrun', 'event')
        depth = 1
