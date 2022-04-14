

## Running Local

### RabbitMQ

- start rabbitmq-server
  - `sudo rabbitmq-server`
- stop rabbitmq-server
  - `sudo rabbitmq-server stop`
  - or `sudo -u rabbitmq rabbitmqctl stop`

### Celery

- activate django env
- activate env variables
- move to project directory

- start worker and beat
  - `celery -A job_scheduler beat -l INFO`
  - `celery -A job_scheduler worker --queues small_task -l INFO -n small_worker@%h`
  - `celery -A job_scheduler worker --queues large_task -l INFO -n large_worker@%h`

- start flower
  - `celery -A job_scheduler flower`


### Celery Beat
When a periodic tasks was removed from the code it is still stored in the database.
Remove the task from Periodic Tasks at the django admin interface.
