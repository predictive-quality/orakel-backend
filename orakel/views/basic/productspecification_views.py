from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ProductSpecificationSerializer
from orakel.models import ProductSpecification


class ProductSpecificationViewSet(CustomModelViewSet):
    """Viewset for Model ProductSpecification.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Relationships:
        Product to ProductSpecification: ManyToOne
        PreProduct to ProductSpecification: ManyToOne
        Event to ProductSpecification: ManyToOne
        ProcessStepSpecification to Productspecification: ManyToOne

    """
    serializer_class = ProductSpecificationSerializer
    django_model = ProductSpecification
