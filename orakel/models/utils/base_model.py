from django.db import models

class BaseModel(models.Model):

    class Meta:
        abstract = True
        ordering = ['-id']
        app_label = 'orakel'



    def __str__(self):
        return self.name