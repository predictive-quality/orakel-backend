# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import os

# Argo Configuration
ARGO_SETTINGS = {
    "ARGO_API_TOKEN": "Bearer " + os.environ.get("ARGO_API_EXEC_TOKEN", " "),
    "ARGO_IP": os.environ.get("ARGO_IP", ""),
    "ARGO_K8_NAMESPACE": os.environ.get("ARGO_K8_NAMESPACE", ""),
}

ARGO_ARTIFACTS_INPUT_PATH = "/code/artifacts/input"
ARGO_ARTIFACTS_OUTPUT_PATH = "/code/artifacts/output"
