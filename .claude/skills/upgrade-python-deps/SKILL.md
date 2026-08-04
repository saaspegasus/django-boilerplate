---
name: upgrade-python-deps
description: Upgrade Python dependencies using uv, then run post-upgrade checks to ensure nothing is broken.
allowed-tools: [
    Bash(uv lock *),
    Bash(uv sync *),
    Bash(make test *),
    Bash(uv run mypy *),
    Bash(sed -i '/^\[options\]$/,/^$/d' uv.lock),
    Bash(grep * uv.lock),
]
---

## Your task

Upgrade all Python dependencies and verify nothing is broken.

### Step 1: Upgrade the lock file

Run `uv lock --upgrade --exclude-newer "7 days"` to upgrade all dependencies to their latest compatible
versions (with a 7-day cooldown to mitigate supply-chain attacks).

Review the output for any resolution errors. If there are conflicts, report them to the user
and ask how to proceed before continuing.

### Step 2: Remove the cooldown marker from the lock file

uv records the `--exclude-newer` cutoff inside `uv.lock` as project configuration. Since it
isn't declared in `pyproject.toml`, any later `uv sync` or `uv run` sees a config mismatch,
discards the lockfile, and silently re-resolves everything to the newest versions — undoing
the cooldown. Prevent this by deleting the `[options]` block at the top of `uv.lock`
(the `exclude-newer` / `exclude-newer-span` lines) before syncing:

```bash
sed -i '/^\[options\]$/,/^$/d' uv.lock
```

The cooldown-resolved versions stay in place; only the marker is removed. Verify with
`grep exclude-newer uv.lock` (should print nothing).

### Step 3: Sync the environment

Run `uv sync` to install the upgraded dependencies into the virtual environment.

### Step 4: Run post-upgrade checks

Run these checks sequentially, stopping if any step fails:
- **Type checking**: Run `uv run mypy .` and report any new type errors. These may be caused
  by updated type stubs or changes in library APIs.
- **Tests**: Run `make test` to verify the test suite still passes.

### Step 5: Summarize and commit

Summarize what was done:
- Which packages were upgraded (notable version changes)
- Whether any type errors were introduced
- Whether all tests passed
- Any issues that need manual attention

If there were failures, present the issues and ask how the user wants to proceed.

If everything passed, ask the user if they'd like to commit the changes. If yes, commit
using the `/commit` skill.
