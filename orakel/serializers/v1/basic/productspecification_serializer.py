# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

from rest_framework.serializers import PrimaryKeyRelatedField as PKF
class ProductSpecificationSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model ProductSpecification.

    Relationships:
        Product to ProductSpecification: ManyToOne
        PreProduct to ProductSpecification: ManyToOne
        Event to ProductSpecification: ManyToOne
        ProcessStepSpecification to Productspecification: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="productspecification-detail", read_only=True)
    product = PrimaryKeyRelatedField(view_name='product-detail',read_only=False, many=True, required=False, queryset=models.Product.objects.all(), style={'base_template': 'input.html'})
    preproduct = PrimaryKeyRelatedField(view_name='preproduct-detail',read_only=False, many=True, required=False, queryset=models.PreProduct.objects.all(), style={'base_template': 'input.html'})
    event= PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})
    processstepspecification = PrimaryKeyRelatedField(view_name='processstepspecification-detail',read_only=False, many=True, required=False, queryset=models.ProcessStepSpecification.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',)

    class Meta:
        model = models.ProductSpecification
        fields = ('id','url','name','description','product','preproduct', 'processstepspecification', 'event')
        depth = 1
