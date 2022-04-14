from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class ProductSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Product

    Relationships:
        ProcessStep to Product: ManyToOne
        Product to ProductSpecification: ManyToOne
        PreProduct to Product: ManyToOne
        Event to Product: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="product-detail", read_only=True)
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False, many=True, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    preproduct = PrimaryKeyRelatedField(view_name='preproduct-detail',read_only=False, many=True, required=False, queryset=models.PreProduct.objects.all(), style={'base_template': 'input.html'})
    productspecification = PrimaryKeyRelatedField(view_name='productspecification-detail',read_only=False, many=False, required=False, queryset=models.ProductSpecification.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',) 

    class Meta:
        model = models.Product
        fields = ('id', 'url', 'name', 'preproduct','processstep', 'productspecification', 'event')
        depth = 1


class PreProductSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model PreProduct.

    Relationships:
        ProcessStep to PreProduct: ManyToOne
        PreProduct to ProductSpecification: ManyToOne
        PreProduct to Product: ManyToOne
        Event to Product: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="preproduct-detail", read_only=True)
    processstep = PrimaryKeyRelatedField(view_name='processstep-detail',read_only=False,  many=True, required=False, queryset=models.ProcessStep.objects.all(), style={'base_template': 'input.html'})
    productspecification = PrimaryKeyRelatedField(view_name='productspecification-detail',read_only=False, many=False, required=False, queryset=models.ProductSpecification.objects.all(), style={'base_template': 'input.html'})
    product = PrimaryKeyRelatedField(view_name='product-detail',read_only=False, many=False, required=False, queryset=models.Product.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False,  many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',) 

    class Meta:
        model = models.PreProduct
        fields = ('id', 'url', 'name', 'product','processstep', 'productspecification', 'event')
        depth = 1