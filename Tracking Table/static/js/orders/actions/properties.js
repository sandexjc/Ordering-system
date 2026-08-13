/*
 * orders/actions/properties.js
 * ----------------------------
 * Public orchestrator that (re)binds all order-detail action handlers.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on (must load first):
 *   - orders/actions/progress-delete.js → setup_progress_delete_handlers
 *   - orders/actions/edit-submit.js     → setup_edit_submit_handlers
 *   - orders/actions/alerts.js          → setup_alert_handlers
 *
 * Used by:
 *   - orders/details/fetch.js (after details load)
 *   - js/dynamic/cache.js (after restoring cached details)
 *
 * Public API name preserved: handle_orders_properties()
 */

/**
 * Re-bind progress/update, delete, edit-submit, and alert handlers.
 * Safe to call multiple times after injecting new detail DOM.
 *
 * @returns {void}
 */
function handle_orders_properties()
{
	setup_progress_delete_handlers();
	setup_edit_submit_handlers();
	setup_alert_handlers();
}
