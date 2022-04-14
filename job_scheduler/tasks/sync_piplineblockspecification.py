# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from Argo.utils import ArgoRequest
from job_scheduler import job_scheduler
from orakel.models import PipelineBlockSpecification
from celery import states
from celery.exceptions import Ignore


class SyncPipeLineBlockSpecification(ArgoRequest):
    """Collect all argo templates that own the label demonstrator and create or update them in form of a PipeLineBlockSpecification instance.
    The task is performed periodically.

    """
    name = "Sync_PipeLineBlockSpecification"
    ignore_result = False # Will save the return value / Task result in the database.
    decription = "Synchronize or create PipeLineBlockSpecification based on argo workflowtemplates."
    queue = "small_task"

    @staticmethod
    def workflow_template_has_demonstrator_label(workflowtemplate):
        """Check if the argo workflow template has a label with the value 'demonstrator'.
        Args:
            workflowtemplate (dict): argo workflow template
        Returns:
            [bool]: True when the labels was found
        """
        # Extract metadata fields from the workflowtemplate
        metadata = workflowtemplate.get("metadata", None)
        # Extract metadata fields from the workflowtemplate
        labels = metadata.get("labels", None)

        if labels:
            return True if "demonstrator" in labels.values() else False
        else:
            return False

    @staticmethod
    def template_has_demonstrator_label(template):
        """Check if the argo_workflow_template.template has the label demonstrator.
        A template is defined as a entrypoint / stage of the workflowtemplate.
        Args:
            template (dict): template of one argo workflow template
        Returns:
            [tuple or None]: Return the template name and the parameters of the template when the label demonstrator was found.
        """
        # Extract metadata fields from the workflowtemplate.template
        metadata = template.get("metadata", None)
        # Extract metadata fields from the workflowtemplate.template
        labels = metadata.get("labels", None)

        if labels:
            if "demonstrator" in labels.keys():
                return (template["name"], template["inputs"]["parameters"])
            else:
                return None

    def run(self, *args, **kwargs):
        """Collect all argo templates that own the label demonstrator and create or update them in form of a PipeLineBlock instance.

        Raises:
            Exception: When the response data could not be read.
            Exception: When the request was not successfull.
            Ignore: Return task.state = Failure when the update/create fails in order to continue and end the process for further databases

        Returns:
            [str]: Amount of created or updated objects and the errors that may occur.
        """
        c_update = 0
        c_create = 0

        # Get all workflowtemplates from argo.
        res = self.make_request("GET", url=self.url_workflowtemplate_get ,data="", max_wait=0, step=1)
        if res.status_code == 200:
            try:
                res_data = res.json()
            except ValueError as e:
                raise Exception("No response data!") from e
        else:
            raise Exception(res.status_code, res.reason)

        # Filter the workflowtemplates. Check if one of the labels has the value demonstrator
        workflow_templates = res_data.get("items", [])
        workflow_templates[:] = [tp for tp in workflow_templates if self.workflow_template_has_demonstrator_label(tp)]
        templates_to_django = []

        # Filter the single templates inside the workflowtemplates. Check if they own a label called demonstrator.
        # The value of the label demonstrator will be the name of the PipeLineBlock
        for workflow_tp in workflow_templates:
            templates = workflow_tp["spec"]["templates"]
            for tp in templates:
                name_parameter = self.template_has_demonstrator_label(tp)
                if name_parameter:
                    templates_to_django.append({"workflow_template": workflow_tp["metadata"]["name"], "name": name_parameter[0], "parameter": name_parameter[1]})

        # Update or create the PipeLineBlocks
        for tp in templates_to_django:
            argo_template_name = tp["workflow_template"]
            argo_template_entrypoint = tp["name"]
            name = argo_template_name + "/" + argo_template_entrypoint
            parameter = [item["name"] for item in tp["parameter"]]
            error = []
            # Apply the templates to each Database
            for db in self.databases:
                try:
                    obj, created = PipelineBlockSpecification.objects.using(db).get_or_create(
                                    name=name,
                                    defaults={  "parameter": parameter,
                                                "argo_template": argo_template_name,
                                                "argo_template_entrypoint": argo_template_entrypoint
                                    }
                    )
                    # Only call save() when the object really has changed. update_or_create() hits the database every time.
                    if created:
                        obj.save()
                        c_create += 1
                    elif obj.parameter != parameter or obj.argo_template != argo_template_name:
                            obj.parameter = parameter
                            obj.argo_template = argo_template_name
                            obj.save()
                            c_update += 1
                except Exception as e:
                    # Only append errors instead of raising exceptions in order to apply changes to all available databases.
                    error.append(e)

        msg = "Created {} and updated {} objects. Error: {}".format(c_create, c_update, error)
        if error:
            self.update_state(state = states.FAILURE, meta = msg)
            raise Ignore()
        else:
            return msg

# Register the task.
job_scheduler.tasks.register(SyncPipeLineBlockSpecification())
