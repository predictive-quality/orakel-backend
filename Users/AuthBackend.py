"""
    OpenID Connect relying party (RP) authentication backends
    =========================================================

    This modules defines backends allowing to authenticate a user using a specific token endpoint
    of an OpenID Connect provider (OP).

"""

import base64
import hashlib

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import SuspiciousOperation
from django.db import transaction
from django.urls import reverse
from django.utils.encoding import force_bytes, smart_text
from django.utils.module_loading import import_string

from .settings import *
from .models import OIDCUser
from .OpenIDBearerAuth import token_to_user

from absl import logging

BASE_64_AUTH = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")).decode("utf-8")



class AuthBackend(ModelBackend):
    """ Allows to authenticate users using an OpenID Connect Provider (OP).

    This authentication backend is able to authenticate users in the case of the OpenID Connect
    Authorization Code flow. The ``authenticate`` method provided by this backend is likely to be
    called when the callback URL is requested by the OpenID Connect Provider (OP). Thus it will
    call the OIDC provider again in order to request a valid token using the authorization code that
    should be available in the request parameters associated with the callback call.

    """

    def authenticate(self, request, *args, **kwargs):
        try:
            logging.info("OPEN ID AUTH")
            nonce = kwargs.get("nonce", None)
            """ Authenticates users in case of the OpenID Connect Authorization code flow. """
            # NOTE: the request object is mandatory to perform the authentication using an authorization
            # code provided by the OIDC supplier.
            if (nonce is None and USE_NONCE) or request is None:
                return

            # Fetches required GET parameters from the HTTP request object.
            state = request.GET.get('state')
            code = request.GET.get('code')

            # Don't go further if the state value or the authorization code is not present in the GET
            # parameters because we won't be able to get a valid token for the user in that case.
            if state is None or code is None:
                raise SuspiciousOperation('Authorization code or state value is missing')

            # Prepares the token payload that will be used to request an authentication token to the
            # token endpoint of the OIDC provider.
            token_payload = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': CALLBACK_URI,
            }

            # Calls the token endpoint.
            token_response = requests.post(TOKEN_ENDPOINT, data=token_payload, verify=SSL_VERIFY)
            token_response.raise_for_status()
            token_response_data = token_response.json()

            # Validates the token.
            raw_id_token = token_response_data.get('id_token')
            #id_token = validate_and_return_id_token(raw_id_token, nonce)

            #if id_token is None:
                #return

            # Retrieves the access token and refresh token.
            access_token = token_response_data.get('access_token')
            refresh_token = token_response_data.get('refresh_token')

            # Stores the ID token, the related access token and the refresh token in the session.
            request.session['oidc_auth_id_token'] = raw_id_token
            request.session['oidc_auth_access_token'] = access_token
            request.session['oidc_auth_refresh_token'] = refresh_token

            # If the id_token contains userinfo scopes and claims we don't have to hit the userinfo
            # endpoint.
            user, _ = token_to_user(access_token)
            return user
        except:
            return None


@transaction.atomic
def create_oidc_user_from_claims(claims):
    """ Creates an ``OIDCUser`` instance using the claims extracted from an id_token. """
    sub = claims['sub']
    email = claims['email']
    username = base64.urlsafe_b64encode(hashlib.sha1(force_bytes(sub)).digest()).rstrip(b'=')
    user = get_user_model().objects.create_user(smart_text(username), email)
    oidc_user = OIDCUser.objects.create(user=user, sub=sub, userinfo=claims)
    return oidc_user


@transaction.atomic
def update_oidc_user_from_claims(oidc_user, claims):
    """ Updates an ``OIDCUser`` instance using the claims extracted from an id_token. """
    oidc_user.userinfo = claims
    oidc_user.save()
    oidc_user.user.email = claims['email']
    oidc_user.user.save()