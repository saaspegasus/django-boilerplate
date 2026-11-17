---
name: pegasus-projects
description: |
  Use when the user asks to create, view, or modify a SaaS Pegasus project
  via the `pegasus` CLI — e.g. "create a new Pegasus project for X",
  "add subscriptions to my Pegasus project", "show me my project settings",
  "switch the front-end framework to React", "what features can I use on
  my license tier".
---

# Managing SaaS Pegasus projects

You are managing a SaaS Pegasus project on behalf of the user. Pegasus is a
Django boilerplate; a "project" is a configuration of features (frontend
framework, auth providers, billing, AI, etc.) that the Pegasus build pipeline
later renders into a real Django codebase. Your job is to translate the user's
intent into the right CLI calls.

## Running the CLI

The Pegasus CLI is published on PyPI as **`pegasus-cli`** (binary name
`pegasus`) and also ships installed in every Pegasus project's venv,
pinned to that project's release version.

**Pick the invocation form at session start:**

1. Run `command -v pegasus`.
2. If it returns a path → **use bare `pegasus ...`**. This is the
   preferred form whenever it's available — the local install is
   version-matched to the project and may even be ahead of what's on
   PyPI (e.g. unreleased CLI changes that ship with the local repo).
3. If it returns nothing → **use `uvx --from pegasus-cli pegasus ...`**
   for every command. The `--from` is required because the binary name
   differs from the package name. Works from any cwd, no venv needed.
   First call caches the env (a few seconds); subsequent calls are
   fast.

**Don't mix forms within a session.** Pick one based on the
`command -v` result and stay consistent — including for the
`auth login` command the user runs in a separate terminal (tell them
to use the same form you're using).

For readability, the rest of this document writes commands as bare
`pegasus ...`. Mentally prepend `uvx --from pegasus-cli` if you're in
the uvx case.

## Setup (one time)

Authentication uses an API key from saaspegasus.com.

- **Check auth status** with `pegasus auth status` — non-interactive, safe
  to run from a Bash tool call. It exits 0 when a key is configured (via
  `~/.pegasus/credentials` or `$PEGASUS_API_KEY`) and non-zero otherwise.
- If unauthenticated, **do not** try to log in from this session.
  `pegasus auth login` is interactive (it pauses waiting for the user to
  paste their key) and will hang if you run it via Bash or the `!` prefix.
  Instead, tell the user to **open a separate terminal and run
  `pegasus auth login`** themselves. They'll be prompted to paste a key
  from https://www.saaspegasus.com/. Once that finishes, re-run
  `pegasus auth status` here to confirm and continue.
- Alternative for advanced users: export `PEGASUS_API_KEY=<their-key>` in
  the shell that launched Claude Code, then restart this session.
- Never try to guess or generate a key yourself — only the user has it.

## Commands

```
pegasus projects list                              # list all projects
pegasus projects fields --json                     # schema for a new project
pegasus projects fields --for <id> --json          # schema for an existing project
pegasus projects show <id> --json                  # full config of one project
pegasus projects create --json [--set k=v ...] [--config-file path]
pegasus projects update <id> --json [--set k=v ...] [--config-file path]
pegasus projects push <id>                         # push to GitHub (separate flow)
```

**ALWAYS pass `--json` when you (an agent) are inspecting output.** The
default is a Rich table for humans that may truncate or scroll past your
visible viewport — a 60+ field schema looks like fields are missing when
they aren't. JSON output is always complete and parseable. Treat tables as
human-only.

## The standard workflow

For any non-trivial create or update, work in this order:

1. **Get the schema.** The endpoint is **project-aware** — call the variant
   that matches your task:
   - **Creating a new project**: `pegasus projects fields --json`
   - **Updating an existing project**: `pegasus projects fields --for <id> --json`

   The schema omits fields the project's release/state can't configure. For
   a new project on a modern release, expect fields like `bundler`,
   `css_framework`, `database`, and `python_package_manager` to be absent
   — there's only one valid choice and the server applies it. For an
   existing legacy project (e.g. one still on `bundler=webpack`), those
   fields reappear with both choices so you can see and change them.
   **Trust what the schema shows.** If `bundler` isn't in the response,
   don't try to set it.

   Response shape:
   ```json
   {
     "user_tier": "free" | "basic" | "pro" | "unlimited",
     "fields": {
       "project_name":        { "type": "string", "max_length": 100 },
       "use_celery":          { "type": "boolean", "min_tier": "free" },
       "use_subscriptions":   { "type": "boolean", "min_tier": "pro" },
       "front_end_framework": {
         "type": "choice",
         "min_tier": "free",
         "choices": [
           { "value": "htmx" },
           { "value": "react", "min_tier": "basic" }
         ]
       },
       ...
     }
   }
   ```

   - **Read `user_tier` first and treat it as a constraint, not a starting
     point.** Build a configuration that fits the user's current tier.
     Don't propose features above their tier unless they explicitly asked
     for one. The default assumption is "stay where you are"; an upgrade
     is something the user opts into, not something you steer them toward.
   - `min_tier` can appear at **two levels** — both must clear the user's
     tier for a value to be usable. Tier ordering is
     `free < basic < pro < unlimited`.
     - **Field-level** (`field.min_tier`): floor to configure the field at
       all. `field.min_tier <= user_tier`.
     - **Per-choice** (`field.choices[i].min_tier`, choice fields only):
       floor to set that specific value. `choice.min_tier <= user_tier`.
       Choices without `min_tier` are always available (assuming the field
       itself is).
   - Fields without `min_tier` (project_name, project_slug, etc.) are
     tier-agnostic.
   - **Choices are objects, not bare strings** — the value to send is at
     `choice.value`. The schema lists every choice regardless of tier and
     tags gated ones with `min_tier`; filter client-side before proposing
     a value to the user. Don't hardcode choice lists, always read them
     from the schema.

2. **If the user explicitly asked for a tier-gated feature they can't use**,
   surface that before attempting the call, and lead with the in-tier path.
   Something like: "Subscriptions requires a Pro license; you're on free.
   I can skip it and build the rest, or if you want to upgrade I can wait."
   Don't bring up upgrades unprompted when the user hasn't asked for
   anything gated.

3. **Construct the payload.** Two ways to provide settings, combinable:
   - `--set key=value` (repeatable) for individual fields. Booleans accept
     `true`/`false`/`yes`/`no`/`y`/`n`. `null`/`none`/empty parse to None
     on the client side, but **most string fields reject null server-side**
     (you'll get `field: This field may not be null.`). Use null only on
     fields explicitly documented as nullable — `pegasus_version` and
     `license` are the main ones.
   - `--config-file path` to load a YAML or JSON file. If the file has a
     `default_context:` top-level key (real `pegasus-config.yaml` shape),
     it's unwrapped automatically. `--set` values override file values.

4. **Call create or update.** The response is the full project in
   `pegasus-config.yaml` shape (see "The config shape" below).

5. **On a 400**, read the response body. Two shapes are possible:
   - **Field-keyed** (DRF serializer errors — bad slug, invalid choice,
     missing required field):
     ```json
     { "project_slug": ["Sorry, your project ID must be a valid Python module name..."] }
     ```
     The CLI renders each as `field: message`.
   - **Flat with optional `help_url`** (business / license errors, e.g.
     a license tier that doesn't support a requested feature):
     ```json
     {
       "error": "Subscriptions is not available on your current license...",
       "help_url": "https://www.saaspegasus.com/billing/"
     }
     ```
     When `help_url` is present, **always relay it to the user** — it's
     where they go to fix the underlying issue (upgrade their license,
     set up a GitHub repo, etc.). The CLI prints it as a second line
     prefixed `More info: <url>`.

   Either way, adjust and retry, or report to the user.

## The config shape

The API speaks the same key shape as a project's local `pegasus-config.yaml`,
with a few specifics:

- **JSON booleans on output**, but input also accepts `"y"`/`"n"` strings —
  so an agent can paste yaml back without translating.
- **Required on create**: only `project_name` and `project_slug`. Everything
  else uses model defaults. `author_name`, `email`, and `license` auto-populate
  from the user's profile if omitted.
- **`project_slug`** must be a valid Python identifier, lowercase, no leading
  or trailing underscore, and not a reserved name (`apps`, `templates`,
  `pegasus`, stdlib module names, etc.). Server normalizes/validates.
- **Renamed wire keys** (different from the model field name):
  - `project_name` ↔ model `name`
  - `use_auto_reload` ↔ model `use_browser_reload`
- **`pegasus_version`** is the *pinned* version (e.g. `"2026.5"` for a
  major release or `"2026.5.1"` for a patch) or `null` to track latest.
  Major versions do *not* have a trailing `.0` — it's `"2026.5"`, not
  `"2026.5.0"`. The value must match an actual released version — the
  server validates against its release list and rejects guessed strings
  like `"2026.5.0"` with `Unknown Pegasus version`. If the user just wants the latest, use
  `null`; don't try to construct a version string. Output also includes
  `_pegasus_version` (read-only, the resolved version that would be
  used at build time).
- **`css_theme`** is a read-only output field derived from `css_framework`.
- **`license`** is a UUID string. Pass `null` for free tier. Must belong to
  the requesting user.

### Read-only fields (output only, ignored on input)

- `id`
- `_pegasus_version` (resolved version)
- `github_username` (computed from the linked GitHub repo or user profile)
- `css_theme` (computed from `css_framework`)

You can safely PATCH the entire GET response back — read-only keys are
silently dropped.

## Defaults you should usually leave alone

The schema decides which choice fields you can touch. Don't try to be clever
about deprecated alternatives — if `bundler` isn't in the schema, the
question "vite or webpack?" doesn't exist for this context. Similarly,
don't ask the user "should we use tailwind or bootstrap?" when the schema
only lists `tailwind`.

For **feature booleans** the user hasn't mentioned, omit them from the
payload — the server applies the model default. Don't enumerate them when
proposing the call; it bloats the conversation. The booleans that default
*on* because they're recommended for typical SaaS apps: `use_sentry`,
`use_health_checks`, `use_impersonation`, `use_async`, `use_celery`,
`use_translations`, `use_browser_reload`, `use_dark_mode`, `use_api_keys`,
`post_process` (ruff). Only flip these to `false` if the user explicitly
asks.

For **AI coding-tool rules** (`use_ai_rules_*`), all default off. If the
user asks for "AI rules" / "agents" generically without naming a tool,
prefer `use_ai_rules_claude=true` (its UI label is "Claude Code
(Recommended)"). Only set `use_ai_rules_agents`, `use_ai_rules_cursor`, or
`use_ai_rules_junie` when the user names that specific tool.

For the **front-end framework**, strongly prefer HTMX. Don't surface React
as an option unprompted — when proposing a project config, just go with
HTMX and move on. Only switch to React if the user explicitly asks for
React, a SPA, or describes a JS-heavy frontend (rich client-side state,
live collaboration, etc.). HTMX is the right default for typical
server-rendered SaaS apps and keeps the project simpler.

## Field interdependencies

The server enforces several couplings. Knowing them keeps you from proposing
conflicting settings:

- `bundler=vite` forces `include_static_files=false`.
- `css_framework != tailwind` forces `use_flowbite=false` and `use_shadcn=false`.
- `use_subscriptions=false` clears `subscription_billing_model` and
  `subscription_pricing_ui`.
- `use_teams=false` clears `use_teams_example`.
- `use_async=false` clears `use_async_example`.

## License × feature gating

License tiers (low to high): `free`, `basic`, `pro`, `unlimited`.

The server validates feature compatibility at create/update time and again
at build time. If a project has features its license can't support, the
API rejects with a 400 keyed per offending feature.

You should pre-check via the schema's `min_tier` rather than discovering
through 400s. If the user wants something their tier can't do, **default
to the in-tier path**:

- Propose the specific subset of gated features to drop, and proceed with
  what their tier supports.
- Only if the user pushes back ("but I really need subscriptions") should
  you surface the upgrade option, and even then as information rather than
  a sales pitch.
- If the user came in *asking* for an upgrade, that's different — help
  them there.

If the user has no license at all and the free tier flag is active for them,
their tier is `free`. Otherwise no license means they can't build at all
(the API will create projects but `pegasus projects push` will refuse).

## Common patterns

**"Create a project for me with X, Y, Z":**
1. Get schema → check user_tier supports X, Y, Z.
2. If anything's gated, tell the user and confirm before proceeding.
3. `pegasus projects create --json --set project_name="..." --set project_slug=... [--set k=v ...]`
4. Show the resulting project to confirm.

**"Show me my project / what's in it":**
- `pegasus projects show <id> --json` and present relevant subset to user.

**"Add feature X" / "switch to React" / etc:**
1. `pegasus projects show <id> --json` to see current state.
2. `pegasus projects fields --for <id> --json` to confirm the field is
   configurable for this project's release/tier.
3. `pegasus projects update <id> --json --set key=value`.

**"Apply these settings from this yaml file":**
- `pegasus projects update <id> --json --config-file path/to/pegasus-config.yaml`.
- Combine with `--set` to override specific values.

**"What can I configure?" / "What features are available?":**
- For a new project: `pegasus projects fields --json`.
- For an existing project: `pegasus projects fields --for <id> --json` —
  the response will reflect that project's release and current values.
- Parse JSON; don't rely on the table.

## Pushing the project

`pegasus projects push <id>` is what actually generates the code — it
renders the project into a linked GitHub repo. It's a separate flow from
create/update.

### Before the first push: connect a GitHub repo

A push will fail with `No GitHub repository configured for this project`
unless a GitHub repo has been linked to the project. **A newly-created
project never has one** — repo linking happens in the Pegasus web UI,
not via the CLI.

When you're about to push a project for the first time, **proactively
tell the user up front** that they need to visit
`https://www.saaspegasus.com/projects/download/<id>/` to connect a
GitHub repo before the push will work. Don't wait for the 400 — flag it
when you confirm "ready to push?" so they don't bounce off an avoidable
error. The same page is where they'd attach a license if their tier
requires one.

### The upgrade prompt (interactive trap)

**The push command is interactive when a newer Pegasus version is
available**, which is essentially always for a freshly-created project.
It prompts:

```
Upgrade options:
  1. Upgrade to latest stable version
  2. Upgrade to latest dev version
  3. Don't upgrade
Select an option (1, 2, 3) [3]:
```

A bare `pegasus projects push <id>` from a Bash tool call will hang on
this prompt and abort. **Always pass one of these flags:**

- `--no-upgrade` — push at the project's currently-pinned Pegasus
  version. This is the right default for a **first push of a
  freshly-created project** (matches option 3, the prompt's default).
- `--upgrade` — upgrade to the latest stable Pegasus version, then push.
- `--dev` — upgrade to the latest dev version, then push.

If the user just created the project and you're pushing for the first
time, default to `--no-upgrade` and don't bring up the upgrade options
unprompted — they picked their version at create time. For pushing an
**existing** project to a newer release (the "upgrade Pegasus" flow), see
the `upgrade-pegasus` skill.

### Setting the PR title (`--pr-title`)

`pegasus projects push` accepts `--pr-title "<text>"` to set the title
of the resulting GitHub PR. **When the push follows a config change,
always pass it** — a good title makes the PR reviewable at a glance,
and the agent has all the context to write one the user won't have to.

The natural title is a short summary of what just changed in
`pegasus projects update`. Examples:

- After `--set front_end_framework=react` →
  `--pr-title "Switch frontend to React"`
- After turning on multiple features →
  `--pr-title "Add subscriptions and teams"`
- After `--set pegasus_version=2026.5.1` →
  `--pr-title "Upgrade Pegasus to 2026.5.1"`

When the change set is large, lead with the headline change rather than
exhaustively listing every flag — the PR diff covers the rest.

For the **first push of a new project**, `--pr-title` is optional;
something like `"Initial Pegasus project setup"` is fine if you want
to set one. For the upgrade-an-existing-project flow, see
`upgrade-pegasus` for title conventions specific to upgrades.

### After a successful push

The push output includes the resulting GitHub repository URL. Once it
completes, **offer to clone the repo locally** (e.g.
`git clone <url> <path>`) so the user can start working on it. Don't
auto-clone — ask first and let them pick the target directory. If
they're not local-dev oriented (e.g. they're pushing from CI or just
wanted the rendered code in GitHub), they'll say no, and that's fine.

## Gotchas

- **Always parse JSON, never the table.** Repeating because it bites:
  `pegasus projects fields` without `--json` is a Rich table that can be
  truncated by terminal height. If you think the schema is "missing" a
  field, you're almost certainly reading truncated output — re-run with
  `--json`.
- **Slug uniqueness is per-user.** Two users can both have a project with
  slug `my_app`. You can't have two on one account.
- **PATCH is partial.** Unspecified fields stay as-is. To "reset" a field,
  you must explicitly set it (e.g., `--set ai_chat_mode=none`).
- **License downgrade can break a project.** If the user PATCHes to a lower
  license tier while pro features are on, the API will 400. Either remove
  the pro features in the same PATCH or do it as two steps.
- **Don't try to discover available choices.** The schema endpoint lists
  every choice for every choice-typed field. Use it.
- **Pegasus build is a separate step.** Creating/updating a project doesn't
  generate any code — that happens via `pegasus projects push` (creates a
  GitHub PR with the rendered project). Build-time validation is stricter
  than create-time validation; if it passes the API it might still fail at
  build with a license/feature/release combo issue.

## Output for the user

Pegasus CLI commands print Rich tables by default. When you're acting as an
agent for a human:

- Show meaningful state changes (the project's new name, the feature you
  changed, etc.), not the entire 60-field config dump.
- Surface license/tier issues clearly — these are conversion moments where
  the user might want to upgrade.
- For multi-step flows (check tier → propose payload → confirm → execute),
  pause at each step rather than running blind.
