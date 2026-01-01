# Architecture
> From [Architecture Revamp #1297]https://github.com/DDMAL/Rodan/issues/1297#issuecomment-2910020124
> and an old wiki document: [Rodan pre-Docker times](https://github.com/DDMAL/Rodan/wiki/Installation-without-Docker)
>
> Refercing a lot from [How Rodan Docker Works](https://github.com/DDMAL/Rodan/wiki/How-Rodan-Docker-Works)
>

## Rodan frontend

Rodan frontend has 3 main components, all Dockerized:
- `nginx` - a reverse proxy server. It also serves the minified version of the web viewer when not working on the frontend.
- `rodan-client` - web viewer, for developing the Rodan-Client front end
- `iipsrv` - a high-performance feature-rich image server for web-based streamed viewing and zooming of ultra high-resolution images (Source: https://github.com/ruven/iipsrv)

Developers can read the READMEs in each folder to work on each components

## Rodan middle layer
### `RabbitMQ` job queue
- RabbitMQ is a message queue to track jobs for `celery` - a Python library used by Rodan for job management.
- When a user "run a job" on the client, a job is queued via RabbitMQ to the backend.

### `Redis` and `PostgreSQL`
- `redis` - a key-value database used by the Rodan server to manage websocket connections. It is used to auto-refresh results on the web interface.
- `postgres-plpython` (inside `postgres` folder) - the PostgreSQL database used by the Rodan server, with the Python extensions installed and custom backup functions.

## Rodan backend: `celery`-related and RESTful API `rodan-main`
- `rodan-main` - the Rodan server providing a REST API.
- `celery` - the Rodan asynchronous task runner. There are different celery services for each queue:
    - Main `celery`: handles basic Rodan tasks, like uploading resources and saving workflows
    - `py3-celery`
    - `gpu-celery`: Rodan GPU-running jobs, such as PACO, Classifier, etc.

