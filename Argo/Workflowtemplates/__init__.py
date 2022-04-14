# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import json

with open("./Argo/Workflowtemplates/base_workflowtemplate.json", "r") as infile:
    BASE_DAG = json.load(infile)
