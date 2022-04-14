import time

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect, QueryDict
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import is_safe_url, urlencode
from django.views.generic import View

from ..settings import *

class OIDCEndSessionView(View):
    """ Allows to end the session of any user authenticated using OpenID Connect.

    This view acts as the main endpoint to end the session of an end-user that was authenticated
    using the OIDC provider (OP). It calls the "end-session" endpoint provided by the provider if
    applicable.

    """

    http_method_names = ['get', 'post', ]

    def get(self, request):
        """ Processes GET requests. """
        return self.post(request)

    def post(self, request):
        """ Processes POST requests. """
        logout_url = LOGOUT_URL or '/'

        # Log out the current user.
        if request.user.is_authenticated:
            try:
                logout_url = self.provider_end_session_url \
                    if END_SESSION_ENDPOINT else logout_url
            except KeyError:  # pragma: no cover
                logout_url = logout_url
            auth.logout(request)

        # Redirects the user to the appropriate URL.

        return HttpResponseRedirect(logout_url)

    @property
    def provider_end_session_url(self):
        """ Returns the end-session URL. """
        q = QueryDict(mutable=True)
        q[END_SESSION_REDIRECT_URI] = \
            self.request.build_absolute_uri(LOGOUT_REDIRECT_URL or '/')
        q[END_SESSION_PARAMETER] = \
            self.request.session['oidc_auth_id_token']
        return '{}?{}'.format(END_SESSION_ENDPOINT, q.urlencode())
