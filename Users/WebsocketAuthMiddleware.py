from .OpenIDBearerAuth import token_to_user
from django.db import close_old_connections


class WebsocketAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        close_old_connections()
        bearer_token = None
        headers = scope["headers"]
        for h in headers:
            if h[0] == b"sec-websocket-protocol":
                bearer_token = h[1].decode("utf-8")
                break
        # print(bearer_token)
        if bearer_token is not None and bearer_token != "None":
            user, _ = token_to_user(bearer_token)
        else:
            user = None
        # scope["user"] = user
        print("MIDDLEWARE PASS {}".format(user))
        return self.inner(scope)
