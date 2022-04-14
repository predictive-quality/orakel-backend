# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from celery.schedules import crontab

# Define periodic tasks

periodic_tasks = {
    "c_update_machine_learning_run_status": {
        "task": "Update_Machine_Learning_Run_Status",
        "schedule": crontab(minute="*/5"),  # Execute every 5 minute.
    },
    "c_sync_pipelineblockspecification": {
        "task": "Sync_PipeLineBlockSpecification",
        "schedule": crontab(minute="*/10"),  # Execute every 10 minutes.
    },
}
