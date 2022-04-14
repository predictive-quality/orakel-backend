# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.db import models

class BaseModel(models.Model):

    class Meta:
        abstract = True
        ordering = ['-id']
        app_label = 'orakel'



    def __str__(self):
        return self.name
