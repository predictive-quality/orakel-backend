# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from absl import logging

class TokenUser:
    def __init__(self, sub, data):
        self.sub = sub
        self.data = data

    def check_roles(self, client_id, roles):
        token_roles = self.data["resource_access"][client_id]["roles"]
        logging.info("Token roles", token_roles)
        for r in roles:
            if r not in token_roles:
                return False
        return True

    @property
    def is_superuser(self):
        return ("superuser" in self.data["realm_access"]["roles"])

    @property
    def is_authenticated(self):
        return self.data["active"]
