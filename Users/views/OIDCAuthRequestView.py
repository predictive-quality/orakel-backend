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

class OIDCAuthRequestView(View):
    """ Allows to start the authorization flow in order to authenticate the end-user.

    This view acts as the main endpoint to trigger the authentication process involving the OIDC
    provider (OP). It prepares an authentication request that will be sent to the authorization
    server in order to authenticate the end-user.

    """

    http_method_names = ['get', ]

    def get(self, request):
        """ Processes GET requests. """
        # Defines common parameters used to bootstrap the authentication request.
        state = get_random_string(STATE_LENGTH)
        authentication_request_params = request.GET.dict()
        authentication_request_params.update({
            'scope': SCOPES,
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'redirect_uri': request.build_absolute_uri(CALLBACK_URI),
            'state': state,
        })

        # Nonces should be used! In that case the generated nonce is stored both in the
        # authentication request parameters and in the user's session.
        if USE_NONCE:
            nonce = get_random_string(NONCE_LENGTH)
            authentication_request_params.update({'nonce': nonce, })
            request.session['oidc_auth_nonce'] = nonce

        # The generated state value must be stored in the user's session for further use.
        request.session['oidc_auth_state'] = state

        # Stores the "next" URL in the session if applicable.
        next_url = request.GET.get('next')
        request.session['oidc_auth_next_url'] = next_url \
            if is_safe_url(url=next_url, allowed_hosts=(request.get_host(), )) else None

        # Redirects the user to authorization endpoint.
        query = urlencode(authentication_request_params)
        redirect_url = '{url}?{query}'.format(
            url=AUTHORIZATION_ENDPOINT, query=query)

        return HttpResponseRedirect(redirect_url)
