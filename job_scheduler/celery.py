# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orakel_api.settings")

# Create celery app
app = Celery("job_scheduler")
# Add config form orakel_api.settings
app.config_from_object(settings, namespace="CELERY")


# Looking for tasks.
# Add class based tasks manually below the class definition.
app.autodiscover_tasks()
