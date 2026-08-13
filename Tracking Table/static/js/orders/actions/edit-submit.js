/*
 * orders/actions/edit-submit.js
 * -----------------------------
 * Edit-form submit buttons with loading state (jQuery).
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on:
 *   - jQuery (global $)
 *
 * Used by:
 *   - orders/actions/properties.js → handle_orders_properties
 */

/**
 * Bind click handlers on `#edit-order-button` and `#edit-vitrine-button`
 * to submit their forms and show a loading spinner on the button.
 *
 * @returns {void}
 */
function setup_edit_submit_handlers()
{
	$('#edit-order-button').click(function() {
		$('#edit-order-form').submit();
		$(this).html("Loading...");
		$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
		$(this).prop('disabled', true);
	})

	$('#edit-vitrine-button').click(function() {
		$('#edit-vitrine-form').submit();
		$(this).html("Loading...");
		$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
		$(this).prop('disabled', true);
	})
}
