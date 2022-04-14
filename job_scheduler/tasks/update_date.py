# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models.basic import ProcessParameter, ProcessStep, QualityCharacteristics, SensorReading
from celery import shared_task
from orakel_api.settings import DATABASES
import datetime

@shared_task(queue="small_task", result=True)
def c_update_date(request):
    """Celery task to update the date of sensorreadings for a given product.

    Returns:
        [Exception]: Returns Exception Message if an error occurs.
    """

    try:
        # get database name from message
        db_name = request.get("database")
        assert db_name in DATABASES.keys(), "No valid database submitted."
        # get data from message
        assert request.get("year")
        year = request.get("year")
        assert request.get("month")
        month = request.get("month")
        assert request.get("day")
        day = request.get("day")
        assert request.get("product_id")
        product_id = request.get("product_id")


        processstep_ids = list(ProcessStep.objects.using(db_name).filter(product_id=product_id).values_list('id'))
        sensorreadings = SensorReading.objects.using(db_name).filter(processstep_id__in=processstep_ids).all()
        for object in sensorreadings:
            object.date = object.date.replace(year=int(year), month=int(month), day=int(day))
            object.save(using=db_name)

    except Exception as e:
        return e.args
