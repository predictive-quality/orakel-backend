from rest_framework.renderers import BrowsableAPIRenderer

from django.template import loader

class NoFilterBrowsableAPIRenderer(BrowsableAPIRenderer):


    def get_filter_form(self, data, view, request):


        if not hasattr(view, 'get_queryset') or not hasattr(view, 'filter_backends'):
            return

        # Infer if this is a list view or not.
        paginator = getattr(view, 'paginator', None)
        if isinstance(data, list):
            pass
        elif paginator is not None and data is not None:
            try:
                paginator.get_results(data)
            except (TypeError, KeyError):
                return
        elif not isinstance(data, list):
            return

        queryset = view.get_queryset()
        elements = []
        # Disable filter for browsable Api
        '''
        for backend in view.filter_backends:
            if hasattr(backend, 'to_html'):

                html = backend().to_html(request, queryset, view)
                if html:
                    elements.append(html)
        ''' 
        if not elements:
            return

        template = loader.get_template(self.filter_template)
        context = {'elements': elements}
        return template.render(context)
