# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from celery import shared_task
import subprocess
from s3_smart_open import from_s3, get_filenames, to_txt, read_txt
import os
import shutil
from datetime import datetime
from io import StringIO

def log_date():
    """Create datetime now string
    Returns:
        [str]: Datetime.now()
    """
    date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S:%MS")
    return date

@shared_task(queue="large_task")
def c_import_fixtures(input_path, database):
    """Import data from fixtures files.

    Args:
        input_path (str): Location of the fixutes. S3 storage path.
        database (str): The database that should load the data/fixutres

    Returns:
        [str]: S3 path to the logfile.
    """

    # Create a log stream in order to upload the logs as logs.txt
    log_stream = StringIO()

    # Name of the temporary directory where the fixtures will be stored.
    tmp_dir = os.path.join("tmp_import_fixtures")

    # Create the temporry directory
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
        created_dir = True
    else:
        created_dir = False

    # Search for files at the input_path and compare them to already loaded fixtures
    filenames = get_filenames(input_path=input_path, file_types=".json")
    try:
        finished_filenames = eval(read_txt(input_path=input_path, filename="finished_filenames.txt"))
    except:
        finished_filenames = []

    log_stream.write("[{}] Already finished files: {}".format(log_date(),finished_filenames))

    # Insert file by file into the database
    for f_name in filenames:
        # Load fixtures which are not in finished_filenames.txt
        if f_name not in finished_filenames:
            log_stream.write("\n[{}] Start: {}".format(log_date(),f_name))
            # Save fixture to the temporary dicretory
            from_s3(input_path=input_path, filename=f_name, output_path=tmp_dir)
            # Command that will load the fixtures
            command = ["python", "manage.py", "loaddata", os.path.join(tmp_dir, f_name), "--database=" + database]
            # Try to insert the data. Successfull fixtures will be added to finished_filenames.txt. When a fixture fails it is added to the log.
            try:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
                finished_filenames.append(f_name)
                to_txt(output_path=input_path, filename="finished_filenames.txt", data=str(finished_filenames))
            except subprocess.CalledProcessError as e:
                output = "Command: " + str(e.cmd) + "\n" + str(e.stdout)

            # Add subprocess outputs and errors to the logs.
            log_stream.write("\n[{}] Load file {}: {}".format(log_date(), f_name, output))

            # Remove fixture file
            if os.path.exists(os.path.join(tmp_dir, f_name)):
                os.remove(os.path.join(tmp_dir, f_name))

            log_stream.write("\n[{}] End: {}".format(log_date(),f_name))

        else:
            log_stream.write("\n[{}] Found {} in finished_filenames.".format(log_date(),f_name))

    # Upload logs to the input_path
    to_txt(output_path=input_path, filename="logs.txt", data=log_stream.getvalue().replace('\n\n', '\n'))

    if created_dir:
        shutil.rmtree(os.path.join(tmp_dir))

    return os.path.join(input_path, "logs.txt")
