# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import time

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import is_safe_url, urlencode
from django.views.generic import View
from ..settings import *

class OIDCAuthErrorView(View):


    http_method_names = ['get', ]

    def get(self, request):
        """ Processes GET requests. """

        return JsonResponse({"description" : "An Error occured during the OpenID Authentication Flow. Please check settings and server!"}, status=401)
