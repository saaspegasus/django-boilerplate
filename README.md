# Django Boilerplate

The original SaaS Boilerplate for Django, trusted by thousands.

## Quickstart

### Prerequisites

To run the app in the recommended configuration, you will need the following installed:
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (for Python)
- [node and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) (for JavaScript)

On Windows, you will also need to install `make`, which you can do by
[following these instructions](https://stackoverflow.com/a/57042516/8207).

### Initial setup

Run the following command to initialize your application:

```bash
make init
```

This will:

- Build and run your Postgres database
- Build and run your Redis database
- Run your database migrations
- Install front end dependencies

Then you can start the app:

```bash
make dev
```

This will run your Django server and build and run your front end (JavaScript and CSS) pipeline.

Your app should now be running! You can open it at [localhost:8000](http://localhost:8000/).

If you're just getting started, [try these steps next](https://docs.saaspegasus.com/getting-started/#post-installation-steps).

### Starting the app

Once initial setup is done, you only need to do the following to start the app in future sessions:

```bash
make start-bg
make dev
```

`make start-bg` starts your Postgres and Redis containers in the background, and `make dev` runs the Django server
and front end pipeline.
If you also need to run Celery, run `make celery` in a separate terminal.

To stop the containers, run `make stop`.

## Using the Makefile

You can run `make` to see other helper functions, and you can view the source
of the file in case you need to run any specific commands.

## Installation - Native

You can also install/run the app directly on your OS using the instructions below.

You can setup a virtual environment and install dependencies in a single command with:

```bash
uv sync
```

This will create your virtual environment in the `.venv` directory of your project root.

## Set up database

*If you are using Docker you can skip these steps.*

Create a database named `project`.

```
createdb project
```

Create database migrations:

```
uv run manage.py makemigrations
```

Create database tables:

```
uv run manage.py migrate
```

## Running server

```bash
uv run manage.py runserver
```

## Building front-end

To build JavaScript and CSS files, first install npm packages:

```bash
npm install
```

Then build (and watch for changes locally):

```bash
npm run dev
```

## Running Celery

Celery can be used to run background tasks.

Celery requires [Redis](https://redis.io/) as a message broker, so make sure
it is installed and running.

You can run it using:

```bash
celery -A project worker -l INFO --pool=solo
```

Or with celery beat (for scheduled tasks):

```bash
celery -A project worker -l INFO -B --pool=solo
```

Note: Using the `solo` pool is recommended for development but not for production.

## Installing Git commit hooks

To install the Git commit hooks run the following:

```shell
uv run pre-commit install --install-hooks
```

Once these are installed they will be run on every commit.

For more information see the [docs](https://docs.saaspegasus.com/code-structure#code-formatting).

## Running Tests

To run tests:

**Using make:**

```bash
make test
```

**Native:**

```bash
uv run manage.py test
```

Or to test a specific app/module:

**Using make:**

```bash
make test ARGS='apps.web.tests.test_basic_views --keepdb'
```

**Native:**

```bash
uv run manage.py test apps.web.tests.test_basic_views --keepdb
```

On Linux-based systems you can watch for changes using the following:

```bash
find . -name '*.py' | entr uv run manage.py test apps.web.tests.test_basic_views
```

---

*Built with [SaaS Pegasus](https://www.saaspegasus.com/), the Django SaaS boilerplate.*
