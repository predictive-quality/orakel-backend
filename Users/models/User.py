# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django import db
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
import six

from .UserManager import UserManager

class User(AbstractUser):
    objects = UserManager()
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()
    username = models.CharField(
        _('username'),
        primary_key=True,
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    roles = models.CharField(max_length=4096, default="")

    def check_roles(self, roles):
        """Compare User.roles with roles.
        """
        user_roles = self.roles.split(" ")
        for r in roles:
            if r not in user_roles:
                return False
        return True

    def check_db_permission(self, db_name):
        """Check if db_name is in User.roles
        """
        user_roles = self.roles.split(" ")
        user_databases = [db[3:] for db in user_roles if db.startswith("db_")]
        return True if db_name in user_databases else False


    def __str__(self):
        name = self.first_name + " " + self.last_name
        if name !=" ":
            return name
        else:
            return self.username
