# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import requests
import base64
from .settings import *
BASE_64_AUTH = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")).decode("utf-8")


def apply_data(user, data):
    first_name = data.get('given_name', "")
    last_name = data.get('family_name', "")
    is_staff = False
    is_superuser = False
    token_roles = []
    if CLIENT_ID in data["resource_access"]:
        token_roles = data["resource_access"][CLIENT_ID]["roles"]
    #realm_roles = data["realm_access"]["roles"]
    if "staff" in token_roles:
        is_staff = True
    if "superuser" in token_roles:
        is_staff = True
        is_superuser = True
    roles = " ".join(token_roles)

    user.first_name = first_name
    user.last_name = last_name
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.roles = roles




def user_update_handler(oidc_user, data):
    django_user = oidc_user.user
    '''
    first_name = data.get('given_name', "")
    last_name = data.get('family_name', "")

    django_user.first_name = first_name
    django_user.last_name = last_name
    '''
    apply_data(django_user, data)
    django_user.save()
