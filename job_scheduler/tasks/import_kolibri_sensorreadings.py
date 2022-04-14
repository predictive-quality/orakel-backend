import datetime
from more_itertools import chunked
from absl import logging
from celery import shared_task
import django

from orakel.models.basic import ProcessParameter, ProcessStep, QualityCharacteristics, SensorReading
from orakel_api.settings import DATABASES


@shared_task(queue="small_task", result=False)
def c_import_kolibri_sensorreadings(sensorreadings):
    """Celery task to import messages from kolibri machine to database.

    Returns:
        [Exception]: Returns Exception Message if an error occurs.
    """
    # Define the batch size
    batch_size = 5000

    try:
        # get database name from message
        db_name = sensorreadings.get("database")
        assert db_name in DATABASES.keys(), "No valid database submitted."
        # get data from message
        data = sensorreadings.get("data")
        assert type(data) == list, "Data submitted in wrong format"
        # create list for database entries to be created with bulk creation
        objs = []
        # for every element in data create sensor reading
        for reading in data:
            # check whether there are data for the necessary values
            assert reading.get("value") != None
            assert reading.get("sensor") != None
            assert reading.get("processstep") != None

            # query for the correct ProcessStepSpecification
            processstepspecification_id = ProcessStep.objects.using(db_name).filter(
                pk=int(reading.get("processstep"))).values_list('processstepspecification_id', flat=True).first()
            logging.debug('Found Processstepspecification in db {}'.format(processstepspecification_id))
            # if there is a ProcessStepSpecification query for ProcessParameter and QualityCharacteristics
            if processstepspecification_id:
                processparameter_id = ProcessParameter.objects.using(db_name).filter(
                    processstepspecification=processstepspecification_id,
                    sensor=int(reading.get("sensor"))).values_list('id', flat=True).first()
                logging.debug('Found processparameter_id in db {}'.format(processparameter_id))
                qualitycharacteristics_id = QualityCharacteristics.objects.using(db_name).filter(
                    processstepspecification=processstepspecification_id,
                    sensor=int(reading.get("sensor"))).values_list('id', flat=True).first()
                logging.debug('Found qualitycharacteristics_id in db {}'.format(qualitycharacteristics_id))
            else:
                logging.debug('processstepspecification_id {} not in db.'.format(processstepspecification_id))
                processparameter_id = None
                qualitycharacteristics_id = None


            # create SensorReading object
            if reading.get("date") == None:
                date = None
            else:
                # check wheter the submitted date is conform to datetime format
                try:
                    date = datetime.datetime.strptime(reading.get("date"), "%Y-%m-%dT%H:%M:%S.%fZ")
                except Exception as e:
                    return e.args
                # Avoid warnings due to missing timezone
                date = django.utils.timezone.make_aware(date)
            # append SensorReading object to objects list
            objs.append(SensorReading(value=float(reading.get("value")), sensor_id=int(reading.get("sensor")),
                                      processstep_id=int(reading.get("processstep")),
                                      qualitycharacteristics_id=qualitycharacteristics_id,
                                      processparameter_id=processparameter_id, date=date))

        # save batches of objects in database
        logging.debug('Generated a batch of {} sensorreadings. Entering into DB now.'.format(len(objs)))
        for batch in list(chunked(objs,batch_size)):
            SensorReading.objects.using(db_name).bulk_create(objs=batch, batch_size=batch_size)
        logging.info('Entered {} sensorreadings into DB.'.format(len(objs)))
    except Exception as e:
        raise e
