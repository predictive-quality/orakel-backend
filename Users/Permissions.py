# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from rest_framework import permissions
from rest_framework import exceptions
import copy


class UserHasRoles(permissions.BasePermission):
    def _permission(self, request, read_roles, full_roles, database_name):
        try:
            if not request.user.is_authenticated:
                return False

            if not request.user.check_db_permission(database_name):
                raise exceptions.PermissionDenied("User {} does not have sufficient roles for database {} in Token!".format(request.auth.sub, database_name))
            if request.user.is_superuser:
                return True
            required_roles = read_roles
            if request.method not in permissions.SAFE_METHODS:
                required_roles = full_roles
            if not request.user.check_roles(required_roles):
                raise exceptions.PermissionDenied("User {} does not have sufficient roles in Token!".format(request.auth.sub))
            else:
                return True

        except Exception as e:
            return False

    def has_permission(self, request, view):
        read_roles = view.read_roles if hasattr(view, "read_roles") else []
        full_roles = view.full_roles if hasattr(view, "full_roles") else []
        database_name = view.kwargs.get('database', None)
        return self._permission(request, read_roles, full_roles, database_name)

    def has_object_permission(self, request, view, obj):
        return True
