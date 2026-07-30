# SaaS Pegasus Django Boilerplate (Open Source Edition)

**The original SaaS boilerplate for Django — trusted by thousands.**

A free, open-source, production-grade starting point for your next Django application. Spin up a
Django app with a modern front-end stack and built-in essentials in minutes.
Optimized for building in the AI-agent era.

This is the **open-source edition** of [SaaS Pegasus](https://www.saaspegasus.com/), the Django SaaS
boilerplate that has powered thousands of startups and products since 2019.
It gives you a real, batteries-included foundation to build on, and a taste of the architecture,
conventions, and tooling used by SaaS Pegasus projects.

> **Looking for more?**
> The pro version of SaaS Pegasus adds Stripe subscriptions, teams &
> multi-tenancy, a host of AI and agent-based capabilities, one-click deployments, and much more.
> **[See everything in SaaS Pegasus Pro →](https://www.saaspegasus.com/)**

## What's included

This boilerplate ships with a complete, modern Django foundation:

- 🐍 **Django 6 on Python 3.14** — a clean, well-organized project structure following Django best practices.
- 🔐 **Authentication** — sign-up, login, password reset, and email verification via [django-allauth](https://docs.allauth.org/).
- ⚡ **HTMX + Alpine.js** — single-page-app interactivity without the single-page-app complexity.
- 🎨 **Tailwind CSS v4 + DaisyUI** — a modern, themeable component library, integrated with [Vite](https://vite.dev/) via [django-vite](https://github.com/MrBin99/django-vite).
- 🔌 **REST API** — built on [Django REST Framework](https://www.django-rest-framework.org/) with an auto-generated, OpenAPI-typed client.
- 🧵 **Background tasks** — [Celery](https://docs.celeryq.dev/) workers and scheduled jobs, backed by Redis.
- 🐘 **Postgres** — the standard Django database, ready to go.
- 🐳 **Docker** — local services (Postgres, Redis) wired up with Docker Compose.
- 🛠️ **Tooling** — Uv for Python, Vite for front end, Ruff formatting/linting, pre-commit hooks, a test suite, and GitHub Actions CI.
- 🤖 **Agent-ready** — ships with `CLAUDE.md`/`AGENTS.md` and built-in skills files, so coding agents understand how to work with the codebase out of the box.

## Custom codebase creator

You can create a free, personalized version of this project using the [SaaS Pegasus codebase creator](https://www.saaspegasus.com/projects/)
(requires signup). This lets you change project details, add/remove features, and change your preferred coding assistant.
You'll also get one-click upgrades and tools for coding agents to configure your project for you.

Don't need customizations? That's fine too, just fork this project and start coding!

## Open-source edition vs. SaaS Pegasus Pro

This repo is a great way to start hobby/personal Django projects and evaluate SaaS Pegasus.
The pro version is more suitable for business-grade SaaS and AI applications.

| Feature | This repo | SaaS Pegasus Pro |
| --- | :---: | :---: |
| Django + Postgres + Celery foundation | ✅ | ✅ |
| Authentication (allauth) | ✅ | ✅ |
| REST API (DRF) | ✅ | ✅ |
| Tailwind + DaisyUI + vite front end | ✅ | ✅ |
| Docker & CI | ✅ | ✅ |
| **Stripe subscriptions & billing** | — | ✅ |
| **Teams & multi-tenancy** | — | ✅ |
| **Built-in AI chat/agent app** | — | ✅ |
| **One-click production deployment** (Render, Fly, Heroku, GCP, AWS…) | — | ✅ |
| **Social & 2FA login, API keys, user impersonation** | — | ✅ |
| **Dedicated support & priority fixes** | Community | ✅ |

**[Check out SaaS Pegasus Pro →](https://www.saaspegasus.com/)**

---

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

## Documentation

This project is built with [SaaS Pegasus](https://www.saaspegasus.com/), and all relevant parts of the
[Pegasus documentation](https://docs.saaspegasus.com/) apply here too.

Splitting out the open-source documentation from the pro documentation is still a work in progress.

## Support

This open-source edition is provided as-is, and is supported by the community. Issues and pull
requests are welcome.

For dedicated support, priority bug fixes, and the full feature set, check out
[SaaS Pegasus](https://www.saaspegasus.com/).
There is also a community Slack instance for all Pegasus Pro customers.

## License

This boilerplate is released under the [MIT License](./LICENSE) — free to use for personal and
commercial projects.
