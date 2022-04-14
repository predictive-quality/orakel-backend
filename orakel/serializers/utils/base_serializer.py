# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from rest_framework.serializers import  HyperlinkedModelSerializer
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject
from rest_framework import relations

from collections import OrderedDict

from .dynamic_fields_serializer import DynamicSerializerMixin

from orakel_api.settings import BASE_API_URL_PATTER


class BaseSerializer(DynamicSerializerMixin, HyperlinkedModelSerializer):
    """HyperlinkedModelSerializer with some customizations.
    Parent serializer class for orakel.serializers.
    """

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields.
    # Be aware of excluding inside the baseclass
    exclude_many_relations_from_filter_url = ()

    def filter_url(self, base_url):
        """Get the url string before the database url kwarg to represent the correct url.

        Args:
            base_url (str): url from build_absolute_uri()

        Returns:
            [str]: first part of the url from the request
        """
        api_string = BASE_API_URL_PATTER
        url = base_url[:base_url.find(api_string)+len(api_string)].rstrip('/') + '/'

        return url

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        Instead of returning lists of related elements, return a url with a filter that returns the list with pagination
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:

            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            # Return an url which includes a filter and enables pagination for the list elements.
            elif type(field) == relations.ManyRelatedField and field.field_name not in self.exclude_many_relations_from_filter_url:
                # Get the api base url in order to append model name and filter name
                base_url = self.filter_url(field.root.context["request"].build_absolute_uri()).rstrip('/')
                url = "{}/{}/{}/?{}={}".format(base_url, self.context['database'],field.field_name, self.Meta.model.__name__.lower(), instance._get_pk_val())
                if attribute.last(): # Check if there is an object available.
                    ret[field.field_name] = {"id": "Inf", "url": url}
                else:
                    ret[field.field_name] = {"id": "NaN", "url": url}
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret
