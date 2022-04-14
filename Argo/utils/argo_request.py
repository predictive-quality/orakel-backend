# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from celery import Task
from orakel import models
import requests
from absl import logging
from time import sleep
from Argo.settings import ARGO_SETTINGS
from orakel_api.settings import DATABASES


class ArgoRequest(Task):
    """BaseClass for celery tasks that need to communicate with Argo.

    Args:
        Task (object): celery.Task
    """
    def __init__(self, *args, **kwargs):
        argo_ip = ARGO_SETTINGS.get("ARGO_IP").rstrip("/")
        k8_namespace = ARGO_SETTINGS.get("ARGO_K8_NAMESPACE")
        self.url_base = argo_ip +  "/api/v1/"
        self.url_workflow_submit = self.url_base + "workflows/" + k8_namespace + "/submit"
        self.url_workflow_put = self.url_base + "workflows/" + k8_namespace
        self.url_get_status_workflow = self.url_base + "workflows/" + k8_namespace + "/"
        self.url_workflowtemplate_get =  self.url_base + "workflow-templates/" + k8_namespace
        self.url_workflowtemplate_post = self.url_base + "workflow-templates/" + k8_namespace
        self.url_workflowtemplate_put = argo_ip + "/workflow-templates/" + k8_namespace.rstrip("/") + "/"

        self.url_delete_workflow = self.url_get_status_workflow
        self.headers = {"Authorization": ARGO_SETTINGS.get("ARGO_API_TOKEN"), "Content-Type": "application/json"}
        self.databases = DATABASES.keys()
        self.decode_status = {k: v for k, v in models.MachineLearningRun.status_choices}

    def __call__(self, *args, **kwargs):
        return self.run(self, *args, **kwargs)

    def make_request(self, request, url, data, max_wait=600, step=5, wait=0):
        """Sends a get, post or delete request every step seconds until the request was successful or wait exceeds max_wait.

        Args:
            request (str): Define which kind of request to execute.
            data (str): Submit information or job_id for a status request or job_id for deleting a trial.
            max_wait (int, optional): Time in seconds after which the requests repetition will be stopped. Defaults to 600.
            step (int, optional): Time in seconds after which a faulty request is repeated. Defaults to 5.
            wait (int, optional): Variable to which the step time is added and compared to max_wait. Defaults to 0.

        Returns:
            [class]: Response
        """

        proxies = {"http": None, "https": None}

        if request == "GET":
            response = requests.get(
                url + data, headers=self.headers, proxies=proxies
            )
        elif request == "POST":
            response = requests.post(
                url, headers=self.headers, data=data, proxies=proxies
            )
        elif request == "DELETE":
            response = requests.delete(
                url + data, headers=self.headers, proxies=proxies
            )
        elif request == "PUT":
            response = requests.put(
                url, headers=self.headers, data=data, proxies=proxies
            )
        else:
            logging.error('Request argument is none of ["GET","POST","DELETE"].')

        if response.status_code == 200 or wait > max_wait:
            if wait > max_wait:
                logging.error("Request has failed for {} seconds with status code: {}:{}".format(max_wait, response.status_code, response.reason))
            return response
        else:
            sleep(step)
            logging.warning("Request has failed for {} times with reason {}:{}".format(1+int((max_wait/step)-((max_wait/step)-(wait/step))), response.status_code, response.reason))
            return self.make_request(request=request, url=url, data=data, max_wait=max_wait,step=step, wait=wait + step, )
