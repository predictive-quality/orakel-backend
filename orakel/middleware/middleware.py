from threadlocals.threadlocals import set_request_variable

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class MultiDbMiddleware(MiddlewareMixin):
    """Specify a threadlocal variable named dbConnection for the database router for every incomming request.
    """    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Get the databasename from the url kwargs
        db_name = view_kwargs.get('database', None)
        set_request_variable('dbConnection', db_name)