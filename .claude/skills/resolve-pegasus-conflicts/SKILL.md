---
name: resolve-pegasus-conflicts
description: Resolve merge conflicts when upgrading SaaS Pegasus. Use when the user has merge conflicts after running git merge during a Pegasus upgrade, or when they need help with the merge process. Also use when the user mentions 'merge pegasus".
---

# Resolve Pegasus Conflicts

## Instructions

This skill helps users resolve merge conflicts when upgrading their SaaS Pegasus codebase. Most users will invoke this skill when they have merge conflicts after merging their main branch into a Pegasus upgrade branch, but you can also help run the merge process for them.

### When invoked

First, determine what the user needs help with by checking their current state:

1. **Check git status**: Run `git status` to see if there's an active merge in progress
2. **Ask the user**: If unclear, ask whether they:
   - Already ran `git merge` and need help resolving conflicts (most common)
   - Want you to run the merge process for them
   - Need help understanding which conflicts to prioritize

### If there's an active merge with conflicts

The user has already run `git merge <main branch>` and has conflicts to resolve. Help them resolve the conflicts using these strategies:

#### Database Migrations

**Principle**: When main/local and Pegasus disagree about a migration, main/local wins. Main's migration files typically reflect what the local DB (and prod) have already applied, so that history is the baseline you protect. When a Pegasus migration *conflicts with or duplicates* something main has already applied, you should drop Pegasus's version in favour of main's, then run `./manage.py makemigrations` to re-express any genuine change as a clean forward diff (the change lives in the merged models, so makemigrations re-derives it).

- **On a conflict**: For conflicted migration files, accept the user's version from main with `git checkout --theirs <migration-file>`, then run `./manage.py makemigrations` after all conflicts are resolved.
- **Watch for silent (conflict-free) migration changes — this is easy to miss**: Pegasus regenerates its own auto-generated migrations and sometimes **renames** them (e.g. `0002_customuser_language...` → `0002_customuser_customer...`). A rename is a delete-on-one-side + add-on-the-other, which git merges with **no conflict markers** — so it slips through silently and leaves you with a duplicate/competing migration the conflict step never flagged. After merging, always diff the migration dirs against main to catch this:
  ```
  git diff --name-status main HEAD -- '*/migrations/*.py'
  ```
  Treat any `R` (rename) the same as a conflict: restore main's file (`git checkout main -- <file>`), delete Pegasus's regenerated copy (`git rm <file>`), then `./manage.py makemigrations` to regenerate the forward diff cleanly. Brand-new app migrations (all `A`, e.g. a freshly added `ecommerce` app) are fine — keep those as-is.
- **djstripe migration references**: If djstripe was upgraded, check if app migrations reference old djstripe migrations that no longer exist (see the "djstripe 2.10 upgrade" section below).

#### Dependency Lock Files (uv.lock, requirements.txt, package-lock.json)
- **Strategy**: Accept Pegasus changes to lock files, merge source files manually
- **Source files**: `pyproject.toml`, `requirements.in`, `package.json`
- **Lock files**: `uv.lock`, `requirements.txt`, `package-lock.json`
- **Action**:
  1. For source files: Merge carefully, keeping customizations
  2. For lock files: Accept ours (Pegasus version) with `git checkout --ours <lock-file>` and `git add <lock-file>`
  3. **Immediately regenerate**: Run `uv sync` (for uv.lock) or `npm install` (for package-lock.json) right after resolving to ensure dependencies are properly synced
- **Important**: Don't wait until post-merge steps - regenerate lock files immediately after resolving them

#### Static Assets (JavaScript/CSS bundles in static/)
- **Strategy**: Delete and regenerate
- **Action**: Accept either version (doesn't matter), will be rebuilt
- **Regenerate**: Run `npm run build` or `npm run dev` after merge

#### Configuration Files (.env.example, settings files)
- **Strategy**: Merge carefully, keep customizations
- **Action**: Review both sides and combine them intelligently

#### Other Files
- **Strategy**: Evaluate case-by-case
- **Action**: Read both versions, understand the changes, merge intelligently

### If running the full merge process

If the user wants you to run the merge:

1. **Fetch latest changes**: Run `git fetch` to download the latest branches and commits from the remote (this ensures you can see the latest Pegasus upgrade branch)
2. **Find the latest upgrade branch**: Run `git branch -a` to list all branches and look for the latest Pegasus upgrade branch (usually prefixed with `pegasus-YYYY.MM`, e.g., `pegasus-2025.01`)
3. **Check current branch**: Run `git status` to see if they're already on the upgrade branch
4. **Checkout the upgrade branch**: If not already on it, run `git checkout <pegasus-branch-name>`
5. **Pull latest changes**: Run `git pull` to ensure the upgrade branch is up to date with the remote
6. **Identify main branch**: Determine the main development branch (usually `main` or `master`)
7. **Run merge**: Execute `git merge <main-branch>` to merge the main development branch into the Pegasus upgrade branch
8. **Handle conflicts**: Follow the conflict resolution strategies above
9. **Dependency sync**: Once conflicts have been resolved, you should re-sync dependencies.
   - Python: `uv sync`
   - JavaScript: `npm install`

### Post-merge steps

After all conflicts are resolved and the merge is complete, run the verification steps below. By default, work straight through them without pausing for confirmation between steps — the user kicked off an upgrade and expects forward motion. Stop only if a step fails, or if the user has said they want to review before pushing.

1. **Frontend install + build**: `npm install && npm run build`
2. **Python dependency sync**: `uv sync`
3. **Migrations**: `./manage.py makemigrations` then `./manage.py migrate`. If `migrate` fails partway, see "Recovering from a partial migration" below.
4. **Tests**: `./manage.py test`
5. **Ruff format + lint**: `make ruff` (auto-formats and auto-fixes lint issues)

Commit any pending changes produced by the steps above (e.g. new migrations, formatting fixes) with a clear message. Docker users can substitute `make upgrade` for the build/migrate steps.

### Recovering from a partial migration

`migrate` commits each migration separately, so a failure partway through can leave earlier migrations applied while a later one fails — the DB is now in a half-migrated state that no longer matches its starting baseline. The local dev DB is typically kept at the same migration state as production, so it matters that you put it back. For Pegasus's schema-only, reversible migrations this is straightforward to undo.

1. **See what actually applied — check, don't theorize.** Surprising schema (tables/columns you didn't expect) is far more likely to be something *you just applied* than pre-existing cruft. Confirm with timestamps:
   ```
   ./manage.py dbshell -- -c "SELECT app, name, applied FROM django_migrations ORDER BY applied DESC LIMIT 20;"
   ```
   The recent timestamps are what this run applied.
2. **Reverse them** back to the last good state, in reverse-dependency order (unapply the app that *depends on* another before the one it depends on):
   ```
   ./manage.py migrate <app> <last_good_migration>   # or `zero` to unapply an app entirely
   ```
3. **If the reverse errors loudly** (e.g. `IrreversibleError` — a data migration with no reverse defined), stop and raise to a human rather than forcing it. Don't pre-gate on `atomic = False` or side effects; just attempt the reverse and let it fail loudly if it can't. (If a forward op already dropped data, that loss happened on apply — reversing won't recover it, and that's also a human escalation.)
4. Once back at a clean baseline, fix the offending migration (see "Database Migrations" above — usually a Pegasus rename/duplicate), then re-run `./manage.py migrate` and confirm the full chain applies cleanly from the baseline.

### Pushing

If everything above passed, the default is to push so the user can open a PR:

```
git push -u origin <branch-name>
```

Then report the branch name and a summary of what was upgraded. The push output includes a "Create a pull request" URL — surface that link to the user and tell them that's where they can review the diff and open the PR.

Hold off on pushing (and ask first) if any of these are true:
- A verification step failed or had warnings worth a human look
- The user said earlier they wanted to review before pushing, or asked to "stop before push"
- The merge required non-trivial judgment calls you're not confident about
- There are local commits unrelated to the upgrade that the user may not want pushed

### Important reminders

- **Enable rerere**: Suggest running `git config rerere.enabled true` to remember conflict resolutions for future upgrades
- **Never squash**: When merging Pegasus PRs in GitHub, always use "Create a merge commit" (not squash or rebase)
- **Review changes**: Always review what changed in the upgrade before committing
- **Always compare clean versions**: When resolving non-trivial conflicts, use `git show HEAD:<file>` and `git show main:<file>` to see the clean versions from each branch, rather than trying to parse the conflict markers in place

### Examples

#### Example 1: User has conflicts (most common)
```
User: "I have merge conflicts after upgrading Pegasus"
You: [Check git status, see conflicts in migrations and uv.lock]
You: "I can see you have conflicts in migrations and uv.lock. Let me help resolve these:
- For migrations: I'll keep your version and we'll regenerate them
- For uv.lock: I'll accept the Pegasus version and regenerate it
[Proceed to resolve conflicts]"
```

#### Example 2: User wants help with the merge
```
User: "Can you help me merge my changes into the Pegasus upgrade branch?"
You: "I can help with that. Let me:
1. Find the latest Pegasus upgrade branch
2. Check out that branch (or confirm you're already on it)
3. Merge your main development branch into it
4. Help resolve any conflicts that come up
[Proceed with finding branch and running git merge main]"
```

### Edge cases

- **No pegasus upgrade branch**: If the user doesn't have a `pegasus-YYYY.MM` branch, direct them to the Pegasus upgrade documentation
- **Too many conflicts**: If there are dozens of conflicts across many files, suggest reviewing them in priority order (migrations first, then lock files, then configuration)
- **Custom modifications**: Be conservative with user customizations - when in doubt, keep their changes and note what was different in Pegasus
- **Unfamiliar file types**: If you encounter conflicts in files you're not sure how to handle, explain both sides of the conflict and ask the user which approach makes sense

### djstripe 2.10 upgrade (Pegasus 2026.2.2+)

Pegasus 2026.2.2 upgraded djstripe from 2.9 to 2.10. This is a significant upgrade that requires extra steps beyond normal conflict resolution.

#### Migration squash
djstripe 2.10 squashed all previous migrations into `0001_initial` and `0002_2_10`. After resolving migration conflicts, check if any app migrations reference old djstripe migrations (e.g. `('djstripe', '0012_2_8')`) that no longer exist. If so, update those dependencies to `('djstripe', '0001_initial')`. Do NOT delete migrations — update their dependency references instead.

#### Fields moved to stripe_data
Many model fields were removed as DB columns and now read from the `stripe_data` JSONField via `@property` accessors. Key changes on `Product`: `default_price`, `type` are now properties. This means:
- `select_related("default_price")` will fail — remove it, just use `.get()` directly
- `filter()`, `order_by()`, `values()` on removed fields will fail — use `stripe_data__<field>` instead
- Property access like `product.default_price.id` still works (it does a DB lookup from `stripe_data`)

#### Re-sync stripe data after migrating
After running `./manage.py migrate`, run `./manage.py djstripe_sync_models Product Price` to repopulate `stripe_data` for existing records. Without this, properties like `product.default_price` will return `None` because the old FK data isn't in `stripe_data` yet.

#### Obsolete workarounds
The `RunSQL` migration that altered `djstripe_paymentintent.capture_method` column length (workaround for [dj-stripe#2038](https://github.com/dj-stripe/dj-stripe/issues/2038)) is no longer needed. Clear its `operations` list (keep the migration file as a no-op for the dependency chain).
