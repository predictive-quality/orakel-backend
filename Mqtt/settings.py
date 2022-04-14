# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import os

MQTT_USER = os.getenv('MQTT_RECEIVER_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_RECEIVER_PASSWORD')
MQTT_BROKER = os.getenv('MQTT_BROKER', '')
MQTT_PORT = os.getenv('MQTT_PORT', 8883)
MQTT_VHOST = os.getenv('MQTT_VHOST', '')

TOPIC_ROOT =  os.getenv('MQTT_KOLIBRI_TOPIC') # Is the same as the kolibri MQTT_USER
TOPIC_SUB = os.getenv('MQTT_KOLIBRI_SUBTOPIC', 'sensorreadings')
