# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import json
import os
import sys
import time

import django
from absl import app, logging
from wzl import mqtt

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orakel_api.settings")
django.setup()

from django.conf import settings as django_settings
import settings as mqtt_settings
from celery import Celery

#logger = mqtt.root_logger.get('Receiver')
job_scheduler = Celery()

def submit_celery_task(topic, sensorreadings):
    sensorreadings = json.loads(sensorreadings)
    if not "database" in sensorreadings:
        logging.warning('Database not in sensorreadings. Rejecting the message.')
        return
    if not "data" in sensorreadings:
        logging.warning('data not in sensorreadings. Rejecting the message.')
        return
    if not type(sensorreadings["data"]) == list:
        logging.warning('data argument in wrong format. Rejecting the message.')
        return

    job_scheduler.send_task('job_scheduler.tasks.import_kolibri_sensorreadings.c_import_kolibri_sensorreadings',
                            [sensorreadings], queue='small_task')
    logging.info("Received {} sensorreading values".format(len(sensorreadings["data"])))


def main(argv):
    # Get mqtt settings and set topic
    user = mqtt_settings.MQTT_USER
    password = mqtt_settings.MQTT_PASSWORD
    broker = mqtt_settings.MQTT_BROKER
    port = int(mqtt_settings.MQTT_PORT)
    vhost = mqtt_settings.MQTT_VHOST
    topic_root = mqtt_settings.TOPIC_ROOT
    topic_sub = mqtt_settings.TOPIC_SUB
    topic = topic_root.rstrip('/') + '/' + topic_sub
    qos = 2  # Receive messages exactly once

    # Set up client
    client_receiver = mqtt.MQTTSubscriber()
    client_receiver.connect(broker, port, vhost + ":" + user, password, ssl=True)
    client_receiver.set_callback("Submit_celery_task", submit_celery_task)
    client_receiver.subscribe(topic, qos)

    # job_scheduler.job_scheduler.config_from_object('django.conf:settings', namespace="CELERY")
    # job_scheduler.job_scheduler.conf.update(broker_url = django_settings.CELERY_BROKER_URL)
    job_scheduler.conf.update(broker_url=django_settings.CELERY_BROKER_URL)
    logging.info("Celery configured at broker {}".format(django_settings.CELERY_BROKER_URL))
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            client_receiver.disconnect()
            break


if __name__ == '__main__':
    app.run(main)
