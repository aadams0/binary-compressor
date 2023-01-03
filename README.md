# Binary File Compressor

*Alex Adams Bodyport Assessment*

## Getting Started

Make sure you have Docker installed.

```shell
docker ps
```

The development version of this application is defined in [docker-compose.yml](docker-compose.yml). Run the following command to start your containers in development mode.

```shell
docker compose up
```

The production version of this application uses a *gunicorn* production server for the Flask application, which is specified in [docker-compose.prod.yml](docker-compose.prod.yml). To run the production version of this appliction, run the following command.

```shell
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

To view the web application, go to [localhost:5000](http://localhost:5000).
To view more information about your RabbitMQ queues, go to [localhost:15672](http://localhost:15672). See [docker-compose.yml](docker-compose.yml) for username and password.

## Application Description 

The Docker compose file starts three images, in startup priority order:

1. A RabbitMQ instance
2. A worker script
3. A Flask application

The worker script initializes the RabbitMQ task queue, handles tasks, and compresses binary files with zlib. The Flask application connects to RabbitMQ on POST to */*. After the Flask application produces a message in the task queue, the worker consumes it and processes the appropriate file. The worker also produces a message to a response queue which the Flask application consumes and uses to render a file download button and file stats.

## Design Choices

- Flask
  - More lightweight compared other opinionated frameworks like Django, which is a good choice for a simple application.
  - Quicker to pick up and build an application from scratch compared to Django
  - Drawbacks
    - Flask is lightweight, so if you decide to add more features to this application (e.g. a full REST API), you may have to opt for third-party libraries or services or build your own.
- RabbitMQ
  - Has a well-supported client library for Python (pika)
  - Support for multiple communication patterns, including the request/reply pattern that is used in this application
  - Guaranteed message delivery and message persistence
  - Has a lot of support for additional security features, which may be important when handling medical data
  - Drawbacks
    - Feature-rich with many configuration options and advanced features, which can be more complex to set up and maintain
    - Disk-based message broker, so it is not as fast as memory-based databases like Redis.
- Docker
  - Easier to deploy applications, given that the host system is compatible with the Docker images
  - Containerizing the application isolates it and its dependencies from the host system, which can make the application more reliable and improve testing quality
  - Improves the portability of application between different environments and systems
  - Drawbacks
    - Requires setup and maintenance of Docker images and configurations
    - May contain resource overhead compared to running an application directly on the host system

I decided against using a frontend framework to reduce the package size and complexity of my code. Utilizing a Flask template with JINJA was sufficient to create the frontend of this application.
