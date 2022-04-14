# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework import serializers

class DataFrameSerializer(BaseSerializer):
    """A model that creates a DataFrame from sensorreadings for a ML-Run.
    A pandas DataFrame will be created after selecting related models in the following order.
    Productspecification --> ProcesStepSpecification --> RealSensor
    When a DataFrame was built, there will be saved a features.fth and target.fth file at the save_path

    Relationships:
        Dataframe to ProductSpecification: ManyToOne
        Dataframe to ProcessStepSpecification: ManyToMany
        Dataframe to ProcessParameter: ManyToMany
        Dataframe to QualityCharacteristics: ManyToMany
        Dataframe to target_value(QualityCharacteristics): ManyToMany
        MachineLearningRunSpecification to DataFrame: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="dataframe-detail", read_only=True)
    qualitycharacteristics = PrimaryKeyRelatedField(view_name='qualitycharacteristics-detail',read_only=False, many=True, required=False, queryset=models.QualityCharacteristics.objects.all(), style={'base_template': 'input.html'})
    processparameter = PrimaryKeyRelatedField(view_name='processparameter-detail',read_only=False, many=True, required=False, queryset=models.ProcessParameter.objects.all(), style={'base_template': 'input.html'})
    processstepspecification = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=True, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})
    productspecification = PrimaryKeyRelatedField(view_name='productspecification-detail',read_only=False, many=False, required=False, queryset=models.ProductSpecification.objects.all(), style={'base_template': 'input.html'})
    target_value = PrimaryKeyRelatedField(view_name='qualitycharacteristics-detail',read_only=False, many=True, required=False, queryset=models.QualityCharacteristics.objects.all(), style={'base_template': 'input.html'})

    status = serializers.CharField(read_only=True)
    product_amount = serializers.IntegerField(required=False, min_value=1, max_value=500000)
    processstepspecification_choice = serializers.SerializerMethodField(method_name="get_processstepspecification_choice")
    processparameter_choice = serializers.SerializerMethodField(method_name="get_processparameter_choice")
    qualitycharacteristics_choice = serializers.SerializerMethodField(method_name="get_qualitycharacteristics_choice")


    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    exclude_many_relations_from_filter_url = ('processstepspecification', 'target_value')

    class Meta:
        model = models.DataFrame
        read_only_fields = ('processstepspecification_choice', 'realsensor_choice')
        fields = ('id','url','name','description', 'status', 'save_path', 'product_amount', 'random_records', 'feature_config','time_series_data', 'productspecification',
                  'processstepspecification', 'processstepspecification_choice', 'qualitycharacteristics', 'processparameter', 'processparameter_choice', 'qualitycharacteristics_choice', 'target_value')
        depth  = 1

    def validate_feature_config(self, value):
        # Ensure that the list only contains one of the allowed_list_values which could be use for the dataframe creation.
        allowed_list_values = ["Min", "Max", "Avg", "StdDev", "StackedDataFrame"]
        if type(value) != list:
            raise serializers.ValidationError("Type {} is not supported for field feature_config. Please provide a list!".format(type(value)))

        for v in value:
            if v not in allowed_list_values:
                raise serializers.ValidationError("Value {} of list is not supported. Allowed list elemets: {}!".format(v,allowed_list_values))

        return value


    def validate_processstepspecification(self, value):
        # Ensure that the processstepspecification intances are related to the dataframe.productspecification
        if hasattr(self, 'instance'):
            pss_choice = self.get_processstepspecification_choice(self.instance)
        else:
            pss_choice = []

        for v in value:
            if hasattr(v, 'pk'):
                if v.pk not in pss_choice:
                    raise serializers.ValidationError("ProcessStepSpecification with id {} is not valid or related to the specified ProductSpecification instance!".format(v.pk))
            else:
                raise serializers.ValidationError("{} has no primary key!".format(v))
        return value

    def validate_processparameter(self, value):
        # Ensure that the processparameter intances are related to the dataframe.processstepspecification
        if hasattr(self, 'instance'):
            pp_choice = self.get_processparameter_choice(self.instance)
        else:
            pp_choice = []

        for v in value:
            if hasattr(v, 'pk'):
                if v.pk not in pp_choice:
                    raise serializers.ValidationError("ProcessParameter with id {} is not valid or not related to one of the specified ProcessStepSpecification instances!".format(v.pk))
            else:
                raise serializers.ValidationError("{} has no primary key!".format(v))
        return value

    def validate_qualitycharacteristics(self, value):
        # Ensure that the qualitycharacteristics intances are related to the dataframe.processstepspecification
        if hasattr(self, 'instance'):
            qc_choice = self.get_qualitycharacteristics_choice(self.instance)
        else:
            qc_choice = []

        for v in value:
            if hasattr(v, 'pk'):
                if v.pk not in qc_choice:
                    raise serializers.ValidationError("QualityCharacteristic with id {} is not valid or not related to one of the specified ProcessSetpSpecification instances!".format(v.pk))
            else:
                raise serializers.ValidationError("{} has no primary key!".format(v))
        return value

    def validate_targetvalue(self, value):
        # Ensure that the target_value(qualitycharacteristics) intances are related to the dataframe.processstepspecification
        return self.validate_qualitycharacteristics(value)

    def get_processstepspecification_choice(self, obj):
        # Get all processstepspecification that are related to the dataframe.productspecification
        if hasattr(obj.productspecification, 'pk'):
            pss = list(models.ProcessStepSpecification.objects.filter(productspecification=obj.productspecification.pk).values_list('pk', flat=True))
        else:
            pss = None
        return pss

    def get_processparameter_choice(self, obj):
        # Get all processparameter that are related to the dataframe.processstepspecification
        pp = []
        for prstsp in obj.processstepspecification.all():
            prstsp_pp = list(models.ProcessStepSpecification.objects.filter(pk=prstsp.pk).values_list('processparameter', flat=True))
            pp.extend(prstsp_pp)

        pp = [x for x in pp if x is not None]
        return set(pp)

    def get_qualitycharacteristics_choice(self, obj):
        # Get all qualitycharacteristics that are related to the dataframe.processstepspecification
        qc = []
        for prstsp in obj.processstepspecification.all():
            prstsp_pp = list(models.ProcessStepSpecification.objects.filter(pk=prstsp.pk).values_list('qualitycharacteristics', flat=True))
            qc.extend(prstsp_pp)

        qc = [x for x in qc if x is not None]
        return set(qc)
