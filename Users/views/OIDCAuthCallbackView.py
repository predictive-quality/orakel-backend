# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

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

class OIDCAuthCallbackView(View):
    """ Allows to complete the authentication process.

    This view acts as the main endpoint to complete the authentication process involving the OIDC
    provider (OP). It checks the request sent by the OIDC provider in order to determine whether the
    considered was successfully authentified or not and authenticates the user at the current
    application level if applicable.

    """

    http_method_names = ['get', ]

    def get(self, request):
        """ Processes GET requests. """
        callback_params = request.GET

        # Retrieve the state value that was previously generated. No state means that we cannot
        # authenticate the user (so a failure should be returned).
        state = request.session.get('oidc_auth_state', None)

        # Retrieve the nonce that was previously generated and remove it from the current session.
        # If no nonce is available (while the USE_NONCE setting is set to True) this means that the
        # authentication cannot be performed and so we have redirect the user to a failure URL.
        nonce = request.session.pop('oidc_auth_nonce', None)

        # NOTE: a redirect to the failure page should be return if some required GET parameters are
        # missing or if no state can be retrieved from the current session.

        if ((nonce and USE_NONCE) or not USE_NONCE) and \
                ('code' in callback_params and 'state' in callback_params) and state:
            # Ensures that the passed state values is the same as the one that was previously
            # generated when forging the authorization request. This is necessary to mitigate
            # Cross-Site Request Forgery (CSRF, XSRF).
            if callback_params['state'] != state:
                raise SuspiciousOperation('Invalid OpenID Connect callback state value')

            # Authenticates the end-user.
            next_url = request.session.get('oidc_auth_next_url', None)
            user = auth.authenticate(nonce=nonce, request=request)

            if user and user.is_active:
                auth.login(self.request, user)
                # Stores an expiration timestamp in the user's session. This value will be used if
                # the project is configured to periodically refresh user's token.
                self.request.session['oidc_auth_id_token_exp_timestamp'] = \
                    time.time() + ID_TOKEN_MAX_AGE
                # Stores the "session_state" value that can be passed by the OpenID Connect provider
                # in order to maintain a consistent session state across the OP and the related
                # relying parties (RP).
                self.request.session['oidc_auth_session_state'] = \
                    callback_params.get('session_state', None)

                return HttpResponseRedirect(
                    next_url or REDIRECT_URI)

        if 'error' in callback_params:
            # If we receive an error in the callback GET parameters, this means that the
            # authentication could not be performed at the OP level. In that case we have to logout
            # the current user because we could've obtained this error after a prompt=none hit on
            # OpenID Connect Provider authenticate endpoint.
            auth.logout(request)

        return HttpResponseRedirect(FAILURE_REDIRECT_URI)
