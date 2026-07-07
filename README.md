# Ordering System

A Django-based production and sales workflow tool for managing furniture-related orders, offers, and vitrine jobs.

## What the system does

The project centralizes day-to-day order handling for three operational streams:

- `Orders`: placed orders (`/internals/`)
- `Offers`: pre-order offers (`/externals/`)
- `Vitrines`: vitrine-specific projects (`/vitrines/`)

Each stream supports searchable dashboards, order editing, progress tracking, printable documents, and historical change visibility.

## Core capabilities

- **Order lifecycle management**
  - Create, edit, update progress, view, print, and soft-delete orders.
  - Track readiness (`order_ready`) and completion (`order_taken`) state.
- **Operational item tracking**
  - Table domain tracks `Plate`, `Edge`, `Cutting`, `Edging`, `Other`, and `Payment` items.
  - Vitrine domain tracks `Frame`, `Glass`, `Hole`, `Seal`, `Other`, and `Payment` items.
- **Automated totals and balances**
  - Item value calculations run through model workflows.
  - Parent order totals and balance are recalculated automatically after relevant changes.
- **Progress and production flow**
  - Plate progress includes ordered/delivered/cutted/edged stages.
  - Edge progress includes ordered/delivered stages.
  - Order-ready logic is derived from item completion state.
- **Audit trail and collaboration context**
  - Notes can be attached to orders.
  - Changes are stored with user, operation, related item, and state transitions.
- **User authentication**
  - Login/logout and user administration pages are included.
  - Main views require authenticated access.

## Technical overview

- **Framework**: Django `5.1.x`
- **Database**: SQLite (default local setup)
- **UI stack**: Django templates + `django-bootstrap5`
- **Apps**:
  - `main`: shared dashboard/search/filter views
  - `accounts`: authentication and user pages
  - `table`: orders/offers domain
  - `vitrine`: vitrine-specific domain logic
  - `common`: reusable base models, querysets, workflows, and views

## Business logic patterns in code

- **Workflow-driven model saves/deletes**
  - Models call `run_workflow_save()` / `run_workflow_delete()`.
  - Domain workflows encapsulate value math, cascading updates, and cleanup.
- **Soft-delete first approach**
  - Shared base models include `deleted_at`.
  - Querysets default to active (non-deleted) records.
- **Composable search/filter dashboard behavior**
  - Search by `ID`, `Client Name`, `Telephone`, or `All`.
  - Fast filter options for recent 100/200/300/500/all entries.

## Key URLs

- `/internals/` - orders board (placed orders)
- `/externals/` - offers board (pre-order offers)
- `/vitrines/` - vitrine orders board
- `/accounts/login/` - authentication
- `/admin/` - Django admin

## Local setup

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure required environment variables

At minimum, set:

- `DJANGO_ENVIRONMENT`
- `DJANGO_SECURITY_ENABLE`
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`

Optional variables supported in settings include:

- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_SESSION_SAVE_EVERY_REQUEST`
- `DJANGO_SESSION_EXPIRE_AT_BROWSER_CLOSE`
- `DJANGO_SESSION_COOKIE_AGE`
- `DJANGO_CSRF_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_AGE`
- `DJANGO_FEATURES__AUTO_SEAL_SELECT`
- `DJANGO_FEATURES__MANUAL_SEAL`

### 4) Run migrations and start the app

```bash
cd "Tracking Table"
python manage.py migrate
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Auto Seal Feature Sync Command

The `vitrine` app provides a management command to align frame auto-seal state with workflow recalculation:

```bash
python manage.py sync_auto_seal --mode <enable-all|sync-selected> [options]
```

Run it from the `Tracking Table` directory, or use `python "Tracking Table/manage.py" ...` from one level above.

### Modes

- `--mode enable-all`
  - Sets `auto_calculate_seal=True` for all matched frames.
  - Recalculates workflow for all matched frames.
- `--mode sync-selected`
  - Recalculates workflow only for matched frames where `auto_calculate_seal=True`.

### Options

- `--dry-run`: preview counts only, no DB writes.
- `--batch-size <N>`: iterator chunk size (default: `1000`).
- `--frame-id <id ...>`: limit processing to specific frame IDs.
- `--vitrine-id <id ...>`: limit processing to frames from specific vitrine IDs.
- `--no-atomic`: disable per-frame `transaction.atomic()`.

### Examples

```bash
# Preview enable-all impact (no writes)
python manage.py sync_auto_seal --mode enable-all --dry-run

# Apply enable-all for specific vitrine IDs
python manage.py sync_auto_seal --mode enable-all --vitrine-id 10 11

# Recalculate only selected frames, in smaller batches
python manage.py sync_auto_seal --mode sync-selected --batch-size 200
```

### Interpreting output

In `enable-all` mode:
- `updated` = frames switched from `auto_calculate_seal=False` to `True`.
- `recalculated` = all matched frames that were processed for workflow recalculation.

So `updated` can be `0` while `recalculated` is still greater than `0`.

## Vitrine Seal Feature Flags

The vitrine seal flow is controlled by two feature flags:

- `DJANGO_FEATURES__AUTO_SEAL_SELECT`
  - Enables frame-level `auto_calculate_seal` selector in edit forms.
  - When enabled, only selected frames generate/update auto seals.
- `DJANGO_FEATURES__MANUAL_SEAL`
  - Enables manual seal mode UI in vitrine edit view.
  - Adds mode switch (`Автоматично` / `Ръчно`) and manual white/black seal inputs.
  - When manual mode is active, order `seals_total` uses:
    - `white_seal_custom_amount * white_seal_price`
    - `black_seal_custom_amount * black_seal_price`
  - Auto-created seal objects per frame are still preserved.

If `DJANGO_FEATURES__MANUAL_SEAL` is disabled, the system always uses seal objects for totals and the manual UI is hidden.
