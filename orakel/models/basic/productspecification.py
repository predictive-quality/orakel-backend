from django.db import models
from orakel.models.utils import BaseModel


class ProductSpecification(BaseModel):
    """The Product Specification holds the product's requirements, tolerances, etc. Essentially, it is a digital specification sheet. 
    There is one Product Specification instance for every product. The Product Specification aggregates all Inter-Product Specifications, if any.

    Relationships:
        Product to ProductSpecification: ManyToOne
        PreProduct to ProductSpecification: ManyToOne
        QualityCharacteristics to ProductSpecification: ManyToOne
        Event to ProductSpecification: ManyToOne
        ProcessStepSpecification to Productspecification: ManyToOne
        
    """

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None ,null=True, blank=True)
