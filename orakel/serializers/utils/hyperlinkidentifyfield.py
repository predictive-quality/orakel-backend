# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from rest_framework.relations import HyperlinkedIdentityField as rf_HyperlinkedIdentityField


class HyperlinkedIdentityField(rf_HyperlinkedIdentityField):
    """
    A read-only field that represents the identity URL for an object, itself.
    This is in contrast to `HyperlinkedRelatedField` which represents the
    URL of relationships to other objects.
    """


    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.
        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        # Add database keyword
        kwargs['database'] = self.context['database']

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
