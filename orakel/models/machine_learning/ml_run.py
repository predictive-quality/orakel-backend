from django.db import models
from orakel.models.utils import BaseModel


class MachineLearningRun(BaseModel):
    """Execution of a MachineLearningRunSpecification with parameter values.
    Relationships:
        MachineLearningRun to MachineLearningRunSpecification: ManyToOne
        Sensor to MachineLearningRun: ManyToOne
        ProcessStepSpecification to MachineLearningRun: OneToOne
    """

    status_choices = (
        ("Pending", "Pending"),
        ("Scheduled", "Scheduled"),
        ("Failed", "Failed"),
        ("Succeeded", "Succeeded"),
        ("Running", "Running"),
        ("Other", "Other"),
    )

    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    status = models.CharField(default="Other", choices=status_choices, max_length=20)
    save_path = models.CharField(max_length=200, blank=True, null=True, default=None)
    parameter = models.JSONField(default=None, null=True, blank=True)
    results = models.JSONField(default=None, null=True, blank=True)
    argo_job_id = models.CharField(max_length=200, default=None, null=True, blank=True)
    deployed = models.BooleanField(default=False, blank=True, null=True)
    inference = models.CharField(max_length=200, default=None, null=True, blank=True)

    # Related fields
    machinelearningrunspecification = models.ForeignKey(
        "MachineLearningRunSpecification",
        related_name="%(class)s",
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
