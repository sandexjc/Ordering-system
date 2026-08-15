# Ordering System

A Django-based production and sales workflow tool for managing furniture-related orders, offers, and vitrine jobs.

## What the system does

The project centralizes day-to-day order handling for two operational boards:

- `table`: table domain board (`/table/`)
- `vitrine`: vitrine domain board (`/vitrine/`)

Each stream supports searchable dashboards, order editing, progress tracking, printable documents, and historical change visibility.

## Core capabilities

- **Order lifecycle management**
  - Create, edit, update progress, view, print, and soft-delete orders.
  - `order_type` marks each order as `order` or `offer`.
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
  - Table order-ready is derived from plate completion (`plates_make_order_ready`).
  - Vitrine order-ready / order-taken are set directly on the vitrine.
  - Static `/table/` and `/vitrine/` update progress through the modal form (`UpdateOrder` / `UpdateVitrine`).
  - Dynamic `/dynamic/` updates table and vitrine progress by clicking a step (`UpdateProgressStep`).
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

- `/table/` - table board (records are filtered by `order_type`)
- `/vitrine/` - vitrine board
- `/dynamic/` - dynamic board (requires `DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING=True`)
- `/accounts/login/` - authentication
- `/admin/` - Django admin

Table progress POST endpoints:

- `/table/updateOrder/<pk>` (`table:update`) - static progress modal form POST
- `/table/updateProgress/<pk>` (`table:update_progress`) - dynamic click-to-toggle JSON POST

Vitrine progress POST endpoints:

- `/vitrine/update_vitrine/<pk>` (`vitrine:update`) - static progress modal form POST
- `/vitrine/update_progress/<pk>` (`vitrine:update_progress`) - dynamic click-to-toggle JSON POST

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
- `DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING`
- `DJANGO_DYNAMIC_CONTENT__SEARCH_MIN_LENGTH`
- `DJANGO_DYNAMIC_CONTENT__SEARCH_DEBOUNCE_MS`
- `DJANGO_DYNAMIC_CONTENT__ORDERS_SYNC_INTERVAL_MS`
- `DJANGO_DYNAMIC_CONTENT__LOCAL_MUTATION_SKIP_MS`
- `DJANGO_DYNAMIC_CONTENT__RANGE_FILTER_DEBOUNCE_MS`
- `DJANGO_DYNAMIC_CONTENT__SYNC_HIGHLIGHT_MS`

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

## Demo Data Commands (beta / local only)

The `common` app provides two management commands for local/demo databases. They are **not intended for production**.

### Seed orders

```bash
python manage.py seed_orders --app <table|vitrine> [--count N] [--locale LOCALE]
```

- `--app` (required): `table` or `vitrine`.
- `--count`: number of orders to create (default: `100`).
- `--locale`: Faker locale (default: `bg_BG`).

What gets created:

- `table`: orders plus plates, edges, and payments.
- `vitrine`: orders plus frames and holes.
- `created_date` values are strictly ascending so they align with sequential order IDs.
- `order_type` is randomly `order` or `offer`, so list pages filtered by type may show fewer than `--count` rows.

Examples:

```bash
python manage.py seed_orders --app table --count 100
python manage.py seed_orders --app vitrine --count 50
```

### Delete orders

```bash
python manage.py delete_orders --app <table|vitrine> (--all | --count N) [--dry-run]
```

- `--app` (required): `table` or `vitrine`.
- `--all`: delete all orders for the selected app.
- `--count N`: delete the `N` newest orders (highest IDs first).
- `--dry-run`: preview how many orders would be deleted, without writing.

Use either `--all` or `--count`, not both.

Deletes are permanent (`hard_delete`), including related items for the targeted orders. Soft-deleted rows are included. On SQLite, autoincrement sequences are reset only when no orders remain for that app.

Examples:

```bash
python manage.py delete_orders --app table --all --dry-run
python manage.py delete_orders --app table --all
python manage.py delete_orders --app table --count 20
python manage.py delete_orders --app vitrine --all
```

Typical local reset:

```bash
python manage.py delete_orders --app table --all
python manage.py delete_orders --app vitrine --all
python manage.py seed_orders --app table --count 100
python manage.py seed_orders --app vitrine --count 100
```

### Keeping these safe on production branches

These commands stay tracked in git (including prod checkouts from master).  
They refuse to run unless `DJANGO_DEBUG=True` (`settings.DEBUG`).

On production, keep `DJANGO_DEBUG=False` so:

```bash
python manage.py seed_orders --app table
python manage.py delete_orders --app table --all
```

both exit with an error and do not touch the database.

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

## Frontend static JS map (`Tracking Table/static/js`)

Shared client scripts live under `Tracking Table/static/js`, grouped by concern. **Public global function names are stable** across files so template `onclick` handlers and cross-file callers keep working.

App-specific assets under `accounts/static`, `vitrine/static`, etc. are outside this map.

### Folder tree

```text
static/js/
  core/
    viewport.js
    boot.js
  orders/
    row-expand/
      transitions.js
      open-close.js
      bind-rows.js
    details/
      spinner.js
      error.js
      fetch.js
    actions/
      progress-delete.js
      progress-step.js     ← dynamic table / vitrine click-to-toggle (loaded from dynamic/orders.html)
      edit-submit.js
      alerts.js
      properties.js      ← handle_orders_properties() orchestrator
      history.js
  dynamic/
    state.js
    filters.js
    search.js
    cache.js
    render.js
    fetch.js
    page.js
```

### Load order

**`main/templates/layout/base.html`**

1. jQuery, Bootstrap
2. `core/viewport.js`
3. `orders/row-expand/{transitions,open-close,bind-rows}.js`
4. `orders/details/{spinner,error,fetch}.js`
5. `orders/actions/{progress-delete,edit-submit,alerts,properties,history}.js`
6. `core/boot.js`
7. optional `vitrine_scripts`

**`main/templates/dynamic/orders.html`** (after `{{ block.super }}`)

1. `dynamic/state.js`
2. `dynamic/filters.js`
3. `dynamic/search.js`
4. `dynamic/cache.js`
5. `dynamic/render.js`
6. `dynamic/fetch.js`
7. `dynamic/page.js`
8. `orders/actions/progress-step.js` (dynamic table / vitrine click-to-toggle; not loaded on static boards)

**Login**

- `accounts/templates/accounts/login.html` → `core/viewport.js` (plus accounts login-base)

### File → main exports

| File | Functions / role |
|------|------------------|
| `core/viewport.js` | `set_viewport_scale` |
| `core/boot.js` | side effects: scale + `handle_orders()` |
| `orders/row-expand/transitions.js` | `_cancelPendingTransitionAndLockHeight`, `onHiddenRowContentUpdated` |
| `orders/row-expand/open-close.js` | `focusClosedOrderRow`, `openHiddenRow`, `closeHiddenRow` |
| `orders/row-expand/bind-rows.js` | `handle_orders` |
| `orders/details/spinner.js` | `add_spinner`, `remove_spinner`, `set_hidden_row_close_visible` |
| `orders/details/error.js` | `create_order_error` |
| `orders/details/fetch.js` | `get_current_dynamic_view_name`, `cache_order_details`, `get_order`, `retry_order` |
| `orders/actions/progress-delete.js` | `setup_progress_delete_handlers`, `apply_progress_update_response`, `sync_progress_step`, `sync_vitrine_order_taken_enabled` |
| `orders/actions/progress-step.js` | click/hover/retry handlers; POSTs one step to `table:update_progress` or `vitrine:update_progress` |
| `orders/actions/edit-submit.js` | `setup_edit_submit_handlers` |
| `orders/actions/alerts.js` | `setup_alert_handlers` |
| `orders/actions/properties.js` | `handle_orders_properties` |
| `orders/actions/history.js` | `handle_orders_history` |
| `dynamic/state.js` | shared cache / timers / constants |
| `dynamic/filters.js` | filters, sort, ranges, counter summary |
| `dynamic/search.js` | search UI + highlight |
| `dynamic/cache.js` | open-row / scroll / details restore, `updateViewCache` |
| `dynamic/render.js` | builders, fade, shell/nav, `setupRenderedRows` |
| `dynamic/fetch.js` | URL, first page, infinite scroll |
| `dynamic/page.js` | `switchDynamicView` + `DOMContentLoaded` |

### Notes for maintainers

- `handle_orders_properties()` orchestrates progress/delete, edit-submit, and alert setup helpers.
- jQuery is still required for `orders/actions/{edit-submit,alerts,history}.js`.
- Keep this map in **developer docs only** (`README.md`). Do not publish it in `PUBLIC.md` or under publicly served `static/` paths.

## Table progress updates (static vs dynamic)

Static `/table/` and dynamic `/dynamic/` share `ViewOrder` (`table:order_view`) but take different update paths.

### Static `/table/` (unchanged)

- Expand a row without `?dynamic=1`.
- Details include the progress modal, plate/edge formsets, `OrderProgressForm`, and the toolbar Update button.
- Submit POSTs to `/table/updateOrder/<pk>` (`UpdateOrder` / `BaseUpdateView`).
- `progress-step.js` is not loaded on this page.

### Dynamic `/dynamic/` (table view)

- Details fetch appends `?dynamic=1`.
- Modal, formsets, and the toolbar Update button are omitted.
- Clicking a progress circle POSTs JSON to `/table/updateProgress/<pk>` (`UpdateProgressStep`).

## Vitrine progress updates (static vs dynamic)

Static `/vitrine/` and dynamic `/dynamic/` share `ViewVitrine` (`vitrine:vitrine_view`).

### Static `/vitrine/` (unchanged)

- Expand a row without `?dynamic=1`.
- Details include the progress modal, `VitrineProgressForm`, and the toolbar Update button.
- Submit POSTs to `/vitrine/update_vitrine/<pk>` (`UpdateVitrine` / `BaseUpdateView`).
- `progress-step.js` is not loaded on this page.

### Dynamic `/dynamic/` (vitrine view)

- Details fetch appends `?dynamic=1`.
- Modal, form, and the toolbar Update button are omitted.
- Clicking **Поръчката е готова** or **Поръчката е взета** POSTs JSON to `/vitrine/update_progress/<pk>`.
- `order_taken` stays disabled until `order_ready` is true (same as `BaseUpdateView` clearing taken when not ready).

### Switching back to the static board

Set `DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING=False`:

- `/` redirects to `/table/` instead of `/dynamic/`.
- `/dynamic/`, `/table/updateProgress/<pk>`, and `/vitrine/update_progress/<pk>` return 404.
- `/table/` keeps the original modal + `table:update` POST.
- `/vitrine/` keeps the original modal + `vitrine:update` POST.

### Backend helpers

| Symbol | Role |
|--------|------|
| `BaseUpdateProgressStepView` | Shared login + CSRF + POST-only JSON toggle, payload parse, field allowlist. |
| `DynamicDetailsModeMixin` | Shared `?dynamic=1` details context (`dynamic_mode`, `progress_update_url`). |
| `table.views.UpdateProgressStep` | Plate/edge sequential updates and order_taken/invoice; same disabled rules as `PlateProgressForm`. |
| `vitrine.views.UpdateProgressStep` | `order_ready` / `order_taken`; taken cannot be set while not ready. |
| `plates_make_order_ready(order)` | True when every plate is delivered, cutted, and edged (empty plate list counts as ready). Shared by `UpdateOrder` and table `UpdateProgressStep`. |
| `apply_progress_update_response` | Applies the JSON payload to row colors and progress-bar `.active` classes. |
| `sync_progress_step` | Toggles one progress `<li>` `.active` / `data-active`. |
| `sync_vitrine_order_taken_enabled` | Enables or disables the vitrine taken step from `order_ready`. |
