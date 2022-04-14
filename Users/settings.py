from django.conf import settings


SYNC_USER_DB = True
USE_NONCE = True
PROVIDER_URI = settings.KEYCLOAK.get("PROVIDER_URI", " ").strip("/") + "/"
APPLICATION_URI = settings.KEYCLOAK.get("APPLICATION_URI", " ").strip("/") + "/"
USERS_PATH = settings.KEYCLOAK.get("USERS_PATH", "users").strip("/")
CLIENT_ID = settings.KEYCLOAK.get('CLIENT_ID', " ")
CLIENT_SECRET = settings.KEYCLOAK.get('CLIENT_SECRET', " ")
REDIRECT_URI = APPLICATION_URI + "api/v1/default/"
TOKEN_ENDPOINT = PROVIDER_URI + "token/"
ID_TOKEN_MAX_AGE = 60
FAILURE_REDIRECT_URI = APPLICATION_URI + USERS_PATH + "/auth/error/"
STATE_LENGTH = 64
AUTHORIZATION_ENDPOINT = PROVIDER_URI + "auth/"
LOGOUT_URL = PROVIDER_URI + "logout/"
LOGOUT_REDIRECT_URL = PROVIDER_URI + "auth/" + "end-session"
END_SESSION_ENDPOINT = PROVIDER_URI + "logout/"
END_SESSION_REDIRECT_URI = APPLICATION_URI
END_SESSION_PARAMETER = "" 
SCOPES = settings.KEYCLOAK.get("SCOPES", "openid profile email")
JWKS_ENDPOINT = PROVIDER_URI + "certs/"
SIGNATURE_ALG = 'HS256'
SIGNATURE_KEY = None
CALLBACK_URI = APPLICATION_URI + USERS_PATH + "/auth/callback/"
NONCE_LENGTH = 64
SSL_VERIFY = False if settings.KEYCLOAK.get("SSL_VERIFY", True) in ["False", "false"] else settings.KEYCLOAK.get("SSL_VERIFY", True)
