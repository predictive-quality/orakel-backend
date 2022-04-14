# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import MachineLearningRunSpecificationSerializer
from orakel import models

from rest_framework.response import Response
from rest_framework import status as rf_status
from rest_framework.decorators import action

from Argo.Workflowtemplates import BASE_DAG
from Argo.settings import ARGO_ARTIFACTS_INPUT_PATH, ARGO_ARTIFACTS_OUTPUT_PATH
from Argo.utils import ArgoRequest

import json


class MachineLearningRunSpecificationViewSet(CustomModelViewSet):
    """Machine Learning Run Specification that has ordered PipeLineBlocks and contains a reference to a DataFrame.
    Cunstruct a case with a combination of PipeLineBlocks that use the linked DataFrame.
    The Model pretend the parameters (without values) for the MachineLearningRun.

    Extra Actions:
        create_template: Queue a job in the scheduler

    Relationships:
        MachineLearningRunSpecification to DataFrame: ManyToOne
        PipelineBlock to MachineLearningRunSpecification: ManyToMany
        MachineLearningRun to MachineLearningRunSpecification: ManyToOne
    """

    serializer_class = MachineLearningRunSpecificationSerializer
    django_model = models.MachineLearningRunSpecification


    def __init__(self, *args, **kwargs):
        super(MachineLearningRunSpecificationViewSet, self).__init__(*args, **kwargs)
        del self.filter_fields["pipeline_order"] # Remove JsonField from filter fields.There is no filter method fpr JsonFields yet.

    def validate_pipeline_order(self, pk):
        """Validation of the pipeline_order format and values.
        Args:
            pk ([type]): pk/id of the PipelineBlock instance
            pipeline_order (dict): keys = identifier for order entries, values = pipelineblock id + dependencies(list of identifier)
        Returns:
            [type]: An error with an error message or none.
        """

        error = False
        error_msg = None
        pipeline_order = self.mlrunspec.pipeline_order
        if type(pipeline_order) == dict:
            # Get related pipelineblocks
            pipelineblocks = set(models.MachineLearningRunSpecification.objects.filter(pk=pk).values_list('pipelineblock', flat=True))
            order_entries = pipeline_order.keys()
            for key, value in pipeline_order.items():
                # Validate Pipelineblock Id
                if 'id' not in value:
                    error = True
                    error_msg = "Order entry with identifier {} has no pipelineblock id".format(key)
                elif value['id'] not in pipelineblocks:
                    error = True
                    error_msg = "Pipelineblock with id {} was not found in the related pipelineblocks!".format(value['id'])
                else:
                    # Validate the dependencies
                    if 'dependencies' not in value:
                        pass
                    elif type(value['dependencies']) != list:
                        error = True
                        error_msg = "TypeError at order entry {}: Dependencies must be list, not {}".format(key, type(value['dependencies']))
                    else:
                        for dep in value['dependencies']:
                            if str(dep) not in order_entries:
                                error = True
                                error_msg = "Dependencies with id {} was not found in the order entries!".format(dep)
                            elif str(dep) == key:
                                error = True
                                error_msg = "Order entry with identifier {} can not have itself as dependency!".format(key)
        else:
            error = True
            error_msg = "TypeError: Must be dict, not {}".format(type(pipeline_order))

        return error, error_msg


    @staticmethod
    def generate_input_output_path(pipeline_order, save_path, df_path):
        """Create input and output path for the pipeline_order elements.

        Args:
            pipeline_order (dict): Pipelineblocks and it's dependecies
            save_path ([type]): Path to save outputs from the last elements of the Dag.
            df_path ([type]): Path where the dataframe is saved.

        Returns:
            [dict]: pipeline_order elements with input and output path
        """

        # find blocks without dependencies
        roots = [key for key, value in pipeline_order.items() if 'dependencies' in value and not value['dependencies']]

        # find blocks that are edges
        deps = []
        for value in pipeline_order.values():
            deps.extend(value['dependencies']) if 'dependencies' in value else None

        edges = list(pipeline_order.keys())
        edges[:] = [x for x in edges if x not in deps]

        # Create path dict with artifacts values as input and output path.
        path_dict = {key: {"input_path": ARGO_ARTIFACTS_INPUT_PATH, "output_path": ARGO_ARTIFACTS_OUTPUT_PATH} for key in  pipeline_order.keys()}

        # Overwrite input path values for blocks which do not consume from artifacts.
        for r in roots:
            path_dict[r]['input_path'] = df_path

        # Overwrite output path values for blocks which do not save to artifacts.
        for e in edges:
            path_dict[e]['output_path'] = save_path

        return path_dict



    def create_template(self, pipeline_order, df_path, wf_tp_name):
        """Create Argo WorkflowTemplate with a main dag. The main dag contains tasks with template references from the pipelineblockspecifications and values from the pipelineblocks
        Args:
            pipeline_order (dict): machinelearningrunspecification.pipeline_order with pipelineblock ids and dependecies.
            df_path (str): Path where the DataFrame is stored.
            wf_tp_name (str): Name of the Workflowtemplate.

        Returns:
            [dict]: Argo WorkflowTemplate
        """
        # Get the base template and generate all paths.
        workflowtemplate = BASE_DAG
        save_path = self.mlrunspec.save_path
        input_output_path = self.generate_input_output_path(pipeline_order, save_path, df_path)

        # Generate all task for the dag
        dag = []
        for key, value in pipeline_order.items():

            task = {}
            # Get the task dependencies, related pipelineblock id and the template informations from the pipelineblockspecification
            pipelineblock_id = value.get('id')
            pipelineblock_dependencies = value.get('dependencies', None)
            pipelineblockspecification = models.PipelineBlockSpecification.objects.get(pipelineblock=pipelineblock_id)

            # Get the parameter values and names from the related pipelineblocks.
            pipelineblock = models.PipelineBlock.objects.get(pk=pipelineblock_id)
            parameter = pipelineblock.parameter

            task['name'] = key
            task['templateRef'] = {'name': pipelineblockspecification.argo_template,'template': pipelineblockspecification.argo_template_entrypoint}
            task['dependencies'] = pipelineblock_dependencies if pipelineblock_dependencies else []
            task['arguments'] = {'parameters': []}

            # Insert parameters
            for para in parameter:
                if para['name'] == 'input_path':
                    para['value'] = input_output_path[key].get("input_path", para['value'])
                elif para['name'] == 'output_path':
                    para['value'] = input_output_path[key].get("output_path", para['value'])

                # Format values that Argo can not handle.
                if para['value'] == None:
                   para['value'] = ""
                elif type(para['value']) == list:
                    para['value'] = ",".join(para['value'])

                task['arguments']['parameters'].append(para)

            # Add artifacts from dependecies.
            if pipelineblock_dependencies:
                task['arguments']['artifacts'] = [{"name": "artifacts-" + str(i),"from": "{{{{tasks.{}.outputs.artifacts.artifacts}}}}".format(pipelineblock_dependencies[i])} for i in range(0, len(pipelineblock_dependencies))]

            dag.append(task)

        workflowtemplate['template']['spec']['templates'][0]['dag']['tasks'] = dag
        workflowtemplate['template']['metadata']['name'] = wf_tp_name

        return workflowtemplate


    @action(detail=True, methods=['get']) # Detail=True to use action/method on an instance.
    def start(self, requests, pk, *args, **kwargs):
        """Create an argo Workflowtemplate in order to submit it.
        Each request will create a new MachineLearningRun instance.

        Args:
            pk (int): id of the machinelearingrunspecification instance.
        """

        self.mlrunspec = models.MachineLearningRunSpecification.objects.get(pk=pk)

        # Assert a save_path in order to start the run.
        if not self.mlrunspec.save_path:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="No save_path found. Please specify a path where the data should be stored.")

        # Check if the dateframe is fine.
        if not hasattr(self.mlrunspec, "dataframe"):
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Please link a dataframe to the instance!")
        elif not self.mlrunspec.dataframe.status == 'Succeeded':
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="The status of the linked datarame is not Succeeded. Please check the Dataframe!")
        else:
            df_path = self.mlrunspec.dataframe.save_path

        # Validate pipeline_order.
        order_not_valid, error_msg = self.validate_pipeline_order(pk)
        if order_not_valid:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data=error_msg)

        # Specify the WorkflowTemplate Name
        wf_tp_name = "dag-" + self.mlrunspec.name
        wf_tp_name = wf_tp_name.lower()

        # Check if the WorkflowTemplate already exists
        argo_request = ArgoRequest()
        url_existing = argo_request.url_workflowtemplate_get.rstrip("/") + "/" + wf_tp_name
        res_existing = argo_request.make_request(request="GET", url=url_existing, data="", max_wait=0, step=0.01)
        if res_existing.status_code == 200:
            wf_exists = True
            # Get dag tasks.
            dag_tasks = json.loads(res_existing.content)['spec']['templates'][0]['dag']['tasks']
        else:
            wf_exists = False

        # Create new template when a related pipelineblock.parameter, the related pipelineblocks, the pipeline_order has changed or the workflowtemplate does not exist.
        if self.mlrunspec.create_new_template or not wf_exists:
            template_to_submit = self.create_template(self.mlrunspec.pipeline_order, df_path, wf_tp_name)
            if wf_exists:
                template_to_submit['template']['metadata'] = json.loads(res_existing.content)['metadata']
                # Put request to update the WorkflowTemplate
                res_create_or_update = argo_request.make_request(request="PUT", url=argo_request.url_workflowtemplate_put , data=json.dumps(template_to_submit), max_wait=0, step=0.01)
            else:
                # Post request to create a new WorkflowTemplate
                res_create_or_update = argo_request.make_request(request="POST", url=argo_request.url_workflowtemplate_post, data=json.dumps(template_to_submit), max_wait=0, step=0.01)
                dag_tasks = template_to_submit['template']['spec']['templates'][0]['dag']['tasks']

            # Return Argo's responce in case of a failure.
            if res_create_or_update.status_code != 200:
                return Response(status=res_create_or_update.status_code, data="WorflowTemplate creation or update has failed. {}".format(res_create_or_update.reason))

            # Save changes
            self.mlrunspec.create_new_template = False
            self.mlrunspec.argo_template = wf_tp_name
            self.mlrunspec.save()

        # Data to sumbit the workflow
        submit_data = json.dumps( {"resourceKind": "WorkflowTemplate",
                                    "resourceName": self.mlrunspec.argo_template,
                                    "submitOptions": {
                                        "entrypoint": "main",
                                        "labels" : "creator=demonstrator"
        }})

        # Start a new Workflow
        res_submit = argo_request.make_request(request="POST", url=argo_request.url_workflow_submit, data=submit_data, max_wait=0, step=0.01)
        # Create a mlrun instance when the workflow was submitted.
        if res_submit.status_code == 200:
            # Get argo job_id
            job_id =  json.loads(res_submit.content)['metadata']['name']
            # Extract the dag task parameter
            mlrun_parameter = {}
            for task in dag_tasks:
                mlrun_parameter[task['name']] = {}
                for para in task['arguments']['parameters']:
                    mlrun_parameter[task['name']][para['name']] = para['value']

            mlrun_data = {"name": job_id, "argo_job_id": job_id, "parameter": mlrun_parameter ,"machinelearningrunspecification_id": pk,"save_path": self.mlrunspec.save_path, "status": "Scheduled"}
            # Create and save the new mlrun instance
            mlrun = models.MachineLearningRun.objects.create(**mlrun_data)
            mlrun.save()

        return Response(status=res_submit.status_code, data=res_submit.reason)
