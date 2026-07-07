# Ordering System - Overview

## What this system is

The Ordering System helps teams manage the full order journey, from initial offer to completed placed order, in one workspace.

## Main workflows

- `Offers`: order offers (pre-order stage, before becoming a placed order)
- `Orders`: placed orders (active production and fulfillment stage)
- `Vitrines`: vitrine-specific projects and execution flow

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

1. Create an offer in `Offers`.
2. When approved, continue as a placed order in `Orders`.
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
