from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import serializers, viewsets
from rest_framework import status as rf_status

from orakel_api.settings import DATABASES

import requests

from Users.settings import CLIENT_ID, CLIENT_SECRET, TOKEN_ENDPOINT, SSL_VERIFY


class BearerTokenFromUserSerializer(serializers.Serializer):
    """Serializer to make the BearerTokenFromUser ViewSet work
    """
    username = serializers.CharField(max_length=500)
    password = serializers.CharField(max_length=500)


class BearerTokenFromUserViewSet(viewsets.ViewSet):
    """The viewset returns a token in order to authenticate requests.
    Username and password are Required.
    """    
    http_method_names = ['post', 'get']
    permission_classes = [ AllowAny]
    serializer_class = BearerTokenFromUserSerializer

    @staticmethod
    def validate_database(database):
        return True if database in DATABASES.keys() else False

    def list(self, request):
            serializer = BearerTokenFromUserSerializer(instance=None, data={"username": None, "password": None})
            serializer.is_valid()
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        
        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username or not password:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Username or password was not supplied!")

        token_payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'password' ,
            'username': username,
            'password': password,
        }

        token_response = requests.post(TOKEN_ENDPOINT, data=token_payload, verify=SSL_VERIFY)
        if token_response.status_code != rf_status.HTTP_200_OK:
            return Response(status=token_response.status_code, data=token_response.reason)

        token_response_data = token_response.json()
        token = token_response_data['access_token']
        expires_in = token_response_data['expires_in']

        return Response(status=rf_status.HTTP_200_OK, data={"token": token, 'expires_in': expires_in})