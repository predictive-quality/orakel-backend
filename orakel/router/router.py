# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from threadlocals.threadlocals import get_request_variable

class MultiDbRouter:
    """Specicy the database to use based on the threadlocal variable dbConnection.
    The variable is set on every incomming request.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'orakel':
            return get_request_variable("dbConnection")
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'orakel':
            return get_request_variable("dbConnection")
        return "default"
