from django.db.models import query
from rest_framework import serializers, relations
from django.urls import NoReverseMatch
from django.core.exceptions import ImproperlyConfigured
from rest_framework.reverse import reverse
from django.db.models.query import QuerySet
from django.db.models import Manager
from rest_framework.exceptions import ErrorDetail, ValidationError

# 
class PrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """This class adds the hyperlinked url to the primary key of the to_representation() method.
    """
    lookup_field = 'pk'

    def __init__(self, view_name=None,  **kwargs):
        # Add attributes to generate the hyperlinked url.
        self.view_name = view_name
        assert self.view_name is not None, 'The `view_name` argument is required.'
        self.lookup_field = kwargs.pop('lookup_field', self.lookup_field)
        self.lookup_url_kwarg = kwargs.pop('lookup_url_kwarg', self.lookup_field)
        self.format = kwargs.pop('format', None)
        self.reverse = reverse

        super().__init__(**kwargs)


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
        kwargs['database'] = self.context['database']

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
    


    def to_representation(self, value):
        assert 'request' in self.context, (
            "`%s` requires the request in the serializer"
            " context. Add `context={'request': request}` when instantiating "
            "the serializer." % self.__class__.__name__
        )

        request = self.context['request']
        format = self.context.get('format')

        # By default use whatever format is given for the current context
        # unless the target is a different type to the source.
        #
        # Eg. Consider a HyperlinkedIdentityField pointing from a json
        # representation to an html property of that representation...
        #
        # '/snippets/1/' should link to '/snippets/1/highlight/'
        # ...but...
        # '/snippets/1/.json' should link to '/snippets/1/highlight/.html'
        if format and self.format and self.format != format:
            format = self.format

        if not hasattr(value, 'pk'):
            return None

        # Return the hyperlink, or error if incorrectly configured.
        try:
            url = self.get_url(value, self.view_name, request, format)
        except NoReverseMatch:
            msg = (
                'Could not resolve URL for hyperlinked relationship using '
                'view name "%s". You may have failed to include the related '
                'model in your API, or incorrectly configured the '
                '`lookup_field` attribute on this field.'
            )
            if value in ('', None):
                value_string = {'': 'the empty string', None: 'None'}[value]
                msg += (
                    " WARNING: The value of the field on the model instance "
                    "was %s, which may be why it didn't match any "
                    "entries in your URL conf." % value_string
                )
            raise ImproperlyConfigured(msg % self.view_name)


        if self.pk_field is not None:
            pk_rep =  self.pk_field.to_representation(value.pk)
        else:
            pk_rep = value.pk

        # Return pk +  hyperlinked url in one string, seperated with a colon.
        return {"id": pk_rep, "url": relations.Hyperlink(url, value)}
