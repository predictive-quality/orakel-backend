from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ProductSerializer, PreProductSerializer
from orakel.models import Product, PreProduct, ProcessStep, ProductSpecification, Event


class ProductViewSet(CustomModelViewSet):
    """Viewset for Model Product.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        ProcessStep to Product: ManyToOne
        Product to ProductSpecification: ManyToOne
        PreProduct to Product: ManyToOne
        Event to Product: ManyToOne

    """
    serializer_class = ProductSerializer
    django_model = Product


class PreProductViewSet(CustomModelViewSet):
    """Viewset for Model PreProduct.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        ProcessStep to PreProduct: ManyToOne
        PreProduct to ProductSpecification: ManyToOne
        PreProduct to Product: ManyToOne
        Event to Product: ManyToOne

    """
    serializer_class = PreProductSerializer
    django_model = PreProduct
