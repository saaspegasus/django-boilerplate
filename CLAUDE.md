# Codebase Guidelines

## Architecture

- This is a Django project built on Python 3.14.
- User authentication uses `django-allauth`.
- The front end is mostly standard Django views and templates.
- HTMX and Alpine.js are used to provide single-page-app user experience with Django templates.
  HTMX is used for interactions which require accessing the backend, and Alpine.js is used for
  browser-only interactions.
- JavaScript files are kept in the `/assets/` folder and built by vite.
  JavaScript code is typically loaded via the static files framework inside Django templates using `django-vite`.
- APIs use Django Rest Framework.
- The front end uses Tailwind (Version 4) and DaisyUI.
- The main database is Postgres.
- Celery is used for background jobs and scheduled tasks.
- Redis is used as the default cache, and the message broker for Celery.

## Commands you can run

The following commands can be used for various tools and workflows.
A `Makefile` is provided to help centralize commands:

```bash
make  # List available commands
```

### First-time Setup

```bash
make init
```

### Starting the Application

Start background services:

```bash
make start     # Run in foreground with logs
make start-bg  # Run in background
```

Start the app:

```bash
make dev       # Run in foreground with logs
```

Access the app at http://localhost:8000

### Stopping Services

Stop background services:

```bash
make stop
```

## Common Commands

### Development

```bash
make shell            # Open Python / Django shell
make dbshell          # Open PostgreSQL shell
make manage ARGS='command'  # Run any Django management command
```

### Database

```bash
make migrations       # Create new migrations
make migrate          # Apply migrations
```

### Testing

```bash
make test                              # Run all tests
make test ARGS='apps.module.tests.test_file'  # Run specific test
make test ARGS='path.to.test --keepdb'        # Run with options
```

### Python Code Quality

```bash
make ruff-format      # Format code
make ruff-lint        # Lint and auto-fix
make ruff             # Run both format and lint
```
### Python

```bash
make uv add '<package>'         # Add a new package
make uv run '<command> <args>'  # Run a Python command
```

### Frontend

```bash
make npm-install      # Install npm packages
make npm-install package-name  # Install specific package
make npm-uninstall package-name  # Uninstall package
make npm-dev          # Run the Vite development server
make npm-build        # Build for production
make npm-type-check   # Run TypeScript type checking
```

Note: Vite runs automatically with hot-reload when using `make dev`.

### Code generation

```bash
make uv run 'pegasus startapp <app_name> <Model1> <Model2Name>'  # Start a new Django app (models are optional)
```

## General Coding Preferences

- Follow the project's existing conventions. Before adding something new, look at how similar functionality is already implemented (e.g. an existing app) and match that pattern rather than introducing a new one.
- Never overwrite the `.env` file without first asking and confirming.
- Don't add mock data to application code. Mocks belong only in tests or test-only utilities.
- Don't add broad `try/except` (or `try/catch`) blocks or fallback values that hide errors. Catch specific exceptions only where you can handle them meaningfully, and let unexpected ones propagate.

## Python Code Guidelines

### Code Style

- Try to use type hints in new code. However, strict type-checking is not enforced and you can leave them out if it's burdensome.
  There is no need to add type hints to existing code if it does not already use them.
- Formatting and import sorting are enforced by ruff (`make ruff`).

### Type annotation conventions

Type checking runs with mypy + django-stubs (`make type-check`). Conventions:

- **Routed views leave `request` unannotated** (all of them, even views that don't touch `request.user`).
  mypy can't see the guarantees made by `@login_required` and similar decorators, so annotating
  `request: HttpRequest` makes accesses like `request.user.<related>` fail type checking.
  Everything that isn't a routed view — middleware, context processors, signal handlers, forms,
  internal helpers — should annotate `request: HttpRequest` normally.
- **In DRF views where a permission class guarantees authentication**, get the typed user via
  `apps.users.helpers.get_authenticated_user(request)` rather than casting `request.user` inline.

### Python 3.14 syntax notes

- **Unparenthesized `except` with multiple exception types is valid** (PEP 758, Python 3.14+).
  `except ValueError, TypeError:` is equivalent to `except (ValueError, TypeError):` — it is **not**
  Python 2 syntax and will **not** raise a `SyntaxError`. Parentheses are still required when using
  `as` (e.g. `except (ValueError, TypeError) as e:`). Do not "fix" unparenthesized forms unless an
  `as` clause is being added.

### Preferred Practices

- Use function-based views by default, unless using a framework that relies on class-based views (e.g. Django Rest Framework).

#### Django models

- All Django models should extend `apps.utils.models.BaseModel` (which adds `created_at` and `updated_at` fields).
- The project's user model is `apps.users.models.CustomUser` and should be imported directly.

## Django Template Coding Guidelines for HTML files

- Indent templates with two spaces.
- For multi-line comments, use `{% comment %}...{% endcomment %}`. The `{# ... #}` syntax is single-line only and does NOT work across multiple lines — never write `{# first line\n   second line #}`.
- JavaScript and CSS files built with vite should be included with the `{% vite_asset %}` template tag provided by `django-vite` (must have `{% load django_vite %}` at the top of the template)
- Any react components also need `{% vite_react_refresh %}` for Vite + React's HMR functionality, from the same `django_vite` template library)
- Use the Django `{% static %}` tag for loading images and external JavaScript / CSS files not managed by vite.
- Avoid inline `<script>` tags where possible.
- Break re-usable template components into separate templates with `{% include %}` statements.
  These normally go into a `components` folder.
- Use DaisyUI styling markup for available components. When not available, fall back to standard TailwindCSS classes.
- Stick with the DaisyUI color palette whenever possible.

## JavaScript Code Guidelines

- Match the existing style: 2-space indentation, single quotes, semicolons.
- Use explicit type annotations in TypeScript files.
- Use Alpine.js for client-side interactivity that doesn't require server interaction.
