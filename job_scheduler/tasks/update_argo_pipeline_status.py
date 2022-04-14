# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from Argo.utils import ArgoRequest
from job_scheduler import job_scheduler
from orakel import models
import json

class UpdateMachineLearningRun(ArgoRequest):
    """Check the argo job status of each MachineLearningRun with status Running or Pending.

    Args:
        ArgoRequest (class): Inhert urls, token, header, available_databases and status from the class

    Returns:
        [type]: [description]
    """
    name = "Update_Machine_Learning_Run_Status"
    decription = "Check the argo job status of each MachineLearingRun with status Running or Pending and apply changes to the MachineLearningRun Instance."
    # Does not save the return value / Task result in the database.
    ignore_result = True  # Does not save the return value / Task result in the database.
    # Assign task to small_worker
    queue = "small_task"

    job_status_to_check = ["Running", "Pending", "Scheduled"]

    def run(self, *args, **kwargs):
        """Check the argo job status of each MachineLearningRun with status in job_status_to_check."""

        for db_name in self.databases:

            try:
                jobs_to_check = list(models.MachineLearningRun.objects.using(db_name).filter(status__in=self.job_status_to_check).values_list('id', 'argo_job_id'))

                for id, job_id in jobs_to_check:
                    response_status = self.make_request(request='GET',url= self.url_get_status_workflow, data=job_id, max_wait=0, step=1)
                    mlrun = models.MachineLearningRun.objects.using(db_name).get(pk=id)
                    if response_status.status_code == 200:
                        status = json.loads(response_status.content)['status']['phase']
                        mlrun.status = self.decode_status.get(status, 'Other')
                    else:
                        mlrun.status = "Other"
                    mlrun.save()
            except:
                pass

# Register class based Task
job_scheduler.tasks.register(UpdateMachineLearningRun())
