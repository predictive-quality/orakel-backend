# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models
from orakel.models.utils import BaseModel

class BaseProduct(BaseModel):
    """Base Class for Product und PreProduct

    Relationships:
        ProcessStep to Pre/Product: ManyToMany
        ProductSpecification to Pre/Product: OneToOne
        Event to Pre/Product: ManyToOne
    """

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    productspecification = models.ForeignKey('ProductSpecification', related_name='%(class)s', default=None, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta(BaseModel.Meta):
        abstract = True




class Product(BaseProduct):
    """A defect-free product is the goal of every production process. It is sold to clients and has to comply with its associated specification.
    A model based on this MMPD creates a new Product instance for every part, which is produced. The instance is associated with its Process Steps.
    While a Product does not contain a lot of information, it serves as an anchor to associate it with all necessary information to enable PQ.

    Relationships:
        ProcessStep to Product: ManyToOne
        Product to ProductSpecification: ManyToOne
        PreProduct to Product: ManyToOne
        Event to Product: ManyToOne
    """

    class Meta(BaseProduct.Meta):
        indexes = [models.Index(fields=['productspecification'])]



class PreProduct(BaseProduct):
    """A Pre-Product is the origin of every manufacturing process.
    Examples are raw materials (e.g. ore), components (e.g. screws) and other necessities (e.g. cooling lubricants).
    Depending on the relationship with the supplier, information about the Pre-Product may be known. If the pre-products are self-supplied, linking the two models supplies additional information.

    Relationships:
        ProcessStep to PreProduct: ManyToOne
        PreProduct to ProductSpecification: ManyToOne
        PreProduct to Product: ManyToOne
        Event to Product: ManyToOne
    """

    product = models.ForeignKey('Product',  related_name='%(class)s', default=None ,null=True, blank=True,on_delete=models.SET_NULL)
