# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.contrib import admin

from .models import User, OIDCUser
admin.site.register(User)
admin.site.register(OIDCUser)
