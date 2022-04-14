from rest_framework import permissions, viewsets

from django.db.models.query import QuerySet

from Users.Permissions import UserHasRoles



class CustomModelViewSet(viewsets.ModelViewSet):
    """Customized ModelViewSet as parent class for orakel.views.
     The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()
    """

    def __init__(self, *args, **kwargs):
        super(CustomModelViewSet, self).__init__(*args, **kwargs)
        self.filter_fields = {f.name: ['exact'] for f in self.django_model._meta.get_fields()}

    permission_classes = (UserHasRoles | permissions.IsAdminUser,)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    read_roles = ['GET', 'HEAD', 'OPTIONS'] 
    full_roles = ['GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'DELETE'] 

    def get_serializer_context(self):
        """Provide the database argument from the url to the serializer context.
        Returns:
            Extra context provivded to the serializer class
        """        
        context = super().get_serializer_context()
        context['database'] = self.kwargs.get('database')
        return context


    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.
        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.
        You may want to override this if you need to provide different
        querysets depending on the incoming request.
        (Eg. return a list of items that is specific to the user)
        """
        queryset = self.serializer_class.Meta.model.objects.all()
        
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        return queryset