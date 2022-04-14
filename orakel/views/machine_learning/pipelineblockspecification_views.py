# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import PipelineBlockSpecificationSerializer
from orakel.models import PipelineBlockSpecification


class PipeLineBlockSpecificationViewSet(CustomModelViewSet):
    """PipelineBlockSpecification that defines a Machine Learning Model or further Pipeline blocks in order to create PipeLineBlocks that include values for the parameter.
    Relationships:
        PipelineBlock to PipeLineBlockSpecifcation: ManyToOne
    """

    serializer_class = PipelineBlockSpecificationSerializer
    django_model = PipelineBlockSpecification

    def __init__(self, *args, **kwargs):
            super(PipeLineBlockSpecificationViewSet, self).__init__(*args, **kwargs)
            del self.filter_fields["parameter"] # Remove JsonField from filter fields.There is no filter method fpr JsonFields yet.
