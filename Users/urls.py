from Users.views.BearerTokenViewSet import BearerTokenFromUserSerializer
from rest_framework import routers
from django.conf.urls import url, include

from .views import UserViewSet, OIDCAuthCallbackView, OIDCAuthRequestView, OIDCEndSessionView, OIDCAuthErrorView, BearerTokenFromUserViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet)
urlpatterns = [
    url(r'^auth/request/$', OIDCAuthRequestView.as_view(), name="oidc_auth_request"),
    url(r'^auth/callback/$', OIDCAuthCallbackView.as_view(), name="oidc_auth_callback"),
    url(r'^auth/end-session/$', OIDCEndSessionView.as_view(), name="oidc_end_session"),
    url(r'^auth/error/$', OIDCAuthErrorView.as_view(), name="oidc_auth_error"),
    url(r'^', include(router.urls)),
    url(r'^auth/token', BearerTokenFromUserViewSet.as_view({"get": "post"}), name="bearertoken")
]
