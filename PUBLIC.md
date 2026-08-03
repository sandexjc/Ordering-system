# Ordering System - Overview

## What this system is

The Ordering System helps teams manage the full order journey, from initial offer to completed placed order, in one workspace.

## Main workflows

- `table`: table domain board (`/table/`) for orders and offers
- `vitrine`: vitrine domain board (`/vitrine/`) for vitrine jobs
- `order_type` controls stage classification (`order` or `offer`)

## What teams can do

- Create and manage customer offers
- Convert and handle placed orders with operational tracking
- Track production progress by item and step
- Monitor pricing, totals, payments, and remaining balance
- Keep notes and change history for better team visibility
- Search and filter work quickly by customer, phone, or order ID

## Why it helps

- Gives a single source of truth for sales and production
- Reduces manual calculation work with automated totals
- Improves traceability through notes and change logs
- Speeds up decision-making with fast search and filtering

## Typical process

1. Create a record with `order_type=offer`.
2. When approved, continue as `order_type=order`.
3. Track progress and updates until completion.
4. Finalize payment and close the order.

## Access

The system is intended for authenticated internal users and supports role-based operational usage through account login.

## Vitrine Seal Feature Operations

For vitrine frames, auto-seal behavior is controlled by the feature flag:

- `DJANGO_FEATURES__AUTO_SEAL_SELECT`
- `DJANGO_FEATURES__MANUAL_SEAL`

Manual seal behavior:

- When `DJANGO_FEATURES__MANUAL_SEAL=true`, users can choose between automatic and manual seal entry in the vitrine edit view.
- In manual mode, order seal totals are calculated from custom white/black seal amounts and seal prices.
- Auto-created seal objects per frame remain preserved for operational consistency.
- When `DJANGO_FEATURES__MANUAL_SEAL=false`, manual seal UI is hidden and totals always come from seal objects.

Operational syncing can be run with:

- `python manage.py sync_auto_seal --mode enable-all`
- `python manage.py sync_auto_seal --mode sync-selected`

Common options:

- `--dry-run` to preview without DB writes
- `--frame-id` / `--vitrine-id` to target specific records
- `--batch-size` to control processing chunk size

## Demo data commands (beta / local only)

For local testing only (requires `pip install faker` for seeding):

- `python manage.py seed_orders --app table|vitrine [--count 100]`
- `python manage.py delete_orders --app table|vitrine (--all | --count N) [--dry-run]`

`seed_orders` creates demo orders with related items (`table`: plates/edges/payments; `vitrine`: frames/holes).  
`delete_orders` permanently removes orders for the selected app (`--all` or newest `--count N`), including related rows, and resets SQLite ID sequences when none remain.

Both commands require `DJANGO_DEBUG=True` and will refuse to run in production when debug is disabled. Keep `Faker` out of production requirements.
