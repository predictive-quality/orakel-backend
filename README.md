# orakel_backend

[Getting started with Django](https://www.djangoproject.com/start/) \
[Getting started with Django Rest Framework](https://www.django-rest-framework.org/tutorial/quickstart/)


## Development of celery tasks

### Celery Periodc Task
When a periodic tasks was removed from the code it will still be scheduled until it is removed from the database.

Remove the task from Periodic Tasks at the django admin interface.

# Installation / Running the App: Cluster

## Preparation for deployment

### Customize application and databases to specific use-case

  1.) orakel_api/settings.py
        - extend the ALLOWED_HOSTS with the application's host (if not localhost)
        - extend the Databases with the for the use-case required databases.
        - extend the CSRF_TRUSTED_ORIGINS with the trusted origins for requests.

  2.) orakel_api/urls.py
      - add e-mail address of contact in line 39
      - add url of application in line 44

  3.) Set up kubernetes Secrets and files
  
  - orakel-backend-secret-key (kubernetes/secret-key.yaml)
      - set correct namespace
      - create a new secret key (python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
      - encode the created secret key to base64 (echo -n "STRING" | base64) and fill it in the "orakel-backend-secret-key" secret under "key".

  - superuser-secret (kubernetes/superuser-secret.yaml)
      - set correct namespace
      - add username, password and e-mail for django-superuser. (NO ENCODING REQUIRED)

  - mysql-secret (kubernetes/mysql/secret.yaml)
      - set correct namespace
      - set root_password, mysql_user, mysql_password and mysql_database for the databases. (ENCODE TO BASE64 as described for orakel-backend-secret-key)

  - argo-api-token (kubernetes/argo/secret.yaml)
      - set correct namespace
      - set the ARGO_API_EXEC_TOKEN as base64 encoded value

  - kubernetes/job_scheduler/deployments/flower.yaml
      - set correct namespace in line 5
      - set authentication for flower in line 42 (--basic_auth=$USERNAME$:$PASSWORD$)

  - kubernetes/mqtt_kolibri/deployment.yaml
      - set "MQTT_RECEIVER_USERNAME", "MQTT_BROKER", "MQTT_VHOST", "MQTT_KOLIBRI_TOPIC"
      - fill the "MQTT_RECEIVER_PASSWORD" as base64 encoded in the secret file (kubernetes/mqtt_kolibri/secret.yaml)

  4.) prepare remaining kubernetes files
  - set correct namespace for remaining deployments, services, configmaps and volumes.
  - create a new volume, deployment and service for each database needed for the specific usecase.
  - add the new databases as environment variables to the following files:
    deployment.yaml, mqtt_kolibri/deployment.yaml, job_scheduler/deployments/beat.yaml, job_scheduler/deployments/flower.yaml, job_scheduler/deployments/worker.yaml

### Setting up Keycloak
  1.) Set up realm and client

  - login to the keycloak admin-console
  - set up a new realm for the application by clicking on "Add realm" and pass it a name.
  - now register the application as a client within the created realm by clicking on "Clients" and then "Create".
  - pass it a "Client ID" (e.g. orakel-backend) and select "openid-conntect" as the Client Protocol.
  - In the Settings tab of the Client switch the access type to confidential and enter a URL scheme of your application in the Valid Redirect URIs field.
  - Enter the base URL of the application in the field Web Origins
  - In the client's Credentials tab select Client Id and Secret as the Client Authenticator and generate a new Secret.


  2.) Set up keycloak.json file
  - fill the values for "realm", "PROVIDER_URI", "APPLICATION_URI", "CLIENT_ID" and "CLIENT_SECRET" based on the above setup and your application setup.


## Deploy Application
  1.) Apply the kubernetes files
  - first deploy all secrets and configmaps
  - create the volumes for the databases
  - deploy the databases
  - apply the memcached deployment
  - apply the backend deployment and service
  - apply the rabbitmq deployment and service
  - apply the celery flower deployment and service
  - apply the celery worker and celery beat deployments
  - apply the mqtt deployment

  2.) Set up the databases
  - access the pod running the backend (kubectl -n $NAMESPACE$ exec --stdin --tty $POD_NAME$ -- /bin/bash)
  - make sure you are in the directory containing the manage.py file
  - create the django migrations by calling python manage.py makemigrations
  - copy the created migrations files to your repository
  - migrate the databases:
    - migrate all apps to the default database by calling python manage.py migrate
    - migrate only the orakel app to all other databases by calling python manage.py migrate --database=$DB_NAME$ orakel


### Add a database
- Expand `DATABASES` in `orakel_api/settings.py`
  - ```
    '$NAME': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("mysql_database", "orakel_backend"),
        'USER': os.getenv("mysql_user", "django_backend_user"),
        'PASSWORD': os.getenv("mysql_password", "django_backend_password"),
        'HOST': os.getenv('DW_DB','127.0.0.5'),
        'PORT': '3306',
    },
    ``` 

- Apply the mysql deployments to the kubernetes cluster


### Debugging

Sometimes it could be usefull to get a shell to the existing server pod. \
    `kubectl -n $namespace exec --stdin --tty $pod-name -- /bin/bash`


# Installation / Running the App: Local

- clone the repository and install the requirements

- install docker in order to run a mysql database
  - [Install on Windows](https://docs.docker.com/docker-for-windows/install/)
  - [Install on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

- create a mysql docker container
  - `docker run --name orakel-backend-mysql-default -p 127.0.0.1:3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_USER=django_backend_user -e MYSQL_PASSWORD=django_backend_password -e MYSQL_DATABASE=orakel_backend -d mysql:latest`

- run `python manage.py makemigrations`
- run `python manage.py migrate`
- the migration could cause an error that it can not remove the index. In this case run the following commands.
  - `python manage.py migrate orakel 0008 --fake`
  - `python manage.py migrate` 
- run `python manage.py runserver` to run the server.
- Follow the instructions displayed to access the web app (either use ```127.0.0.1:8000``` or ```localhost:8000``` in your web browser).
- You can login with a non keycloak account via the admin Ui 127.0.0.1:8000/admin. Username=root, password=password.


### Add a database
- Expand `DATABASES` in `orakel_api/settings.py`
  - ```
    '$NAME': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("mysql_database", "orakel_backend"),
        'USER': os.getenv("mysql_user", "django_backend_user"),
        'PASSWORD': os.getenv("mysql_password", "django_backend_password"),
        'HOST': os.getenv('DW_DB','127.0.0.5'),
        'PORT': '3306',
    },
    ``` 

- create docker container with an mysql image
  - - create a mysql docker container
  - `docker run --name orakel-backend-mysql-$NAME -p IP:3306:$PORT -e MYSQL_ROOT_PASSWORD=password -e MYSQL_USER=django_backend_user -e MYSQL_PASSWORD=django_backend_password -e MYSQL_DATABASE=orakel_backend -d mysql:latest`
