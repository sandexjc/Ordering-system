/*
 * orders/actions/alerts.js
 * ------------------------
 * Success / error alert dismiss buttons and focus (jQuery).
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
 * Bind dismiss clicks for success/error alert banners and focus `.alertmsg` if present.
 *
 * @returns {void}
 */
function setup_alert_handlers()
{
	$(".SuccessAlertBtn").click(function() {
		$(".ALERT-S-UPD-VIEW").css("display","none");
		$(".ALERT-S-DEL-VIEW").css("display","none");
	})

	$(".ErrorAlertBtn").click(function() {
		$(".ALERT-E-UPD-VIEW").css("display","none");
		$(".ALERT-E-DEL-VIEW").css("display","none");
	})

	$(".alertmsg").focus();
}
