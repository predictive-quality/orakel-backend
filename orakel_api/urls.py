# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

"""orakel_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from .settings import STATIC_ROOT, BASE_API_URL_PATTER

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required
from decorator_include import decorator_include

from Users.Permissions import UserHasRoles
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="Demonstator Backend API",
      default_version='v1',
      description="",
      contact=openapi.Contact(email=""),

   ),
   public=False,
   permission_classes=(UserHasRoles| permissions.IsAdminUser,),
   url='',
   patterns=[path('api/v1/default/',include(('orakel.urls','orakel'), namespace='v1'))]
)



urlpatterns = [

    #re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': STATIC_ROOT}),

    path('admin/', admin.site.urls),

    path(BASE_API_URL_PATTER +'<str:database>/',include(('orakel.urls','orakel'), namespace='v1')),


    re_path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # re_path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('users/', include("Users.urls")),

    # re_path('api/v2/',include(('orakel.urls','orakel'), namespace='v2')),

    path('plate/', decorator_include(login_required, 'django_spaghetti.urls')),
]
