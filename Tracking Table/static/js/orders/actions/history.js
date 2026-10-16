/*
 * orders/actions/history.js
 * -------------------------
 * Order history offcanvas loader (jQuery + $.ajax).
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on:
 *   - jQuery (global $)
 *
 * Used by:
 *   - orders/details/fetch.js (after details load)
 *   - js/dynamic/cache.js (after restoring cached details)
 *   - the history button and the refresh button in the history panel
 */

/**
 * History URL stored on the toolbar button.
 *
 * @param {string|number} orderId
 * @returns {string}
 */
function historyUrlFor(orderId)
{
	const button = document.getElementById("btn-history-" + orderId);
	if (!button) {
		return "";
	}
	return button.getAttribute("data-history-url") || "";
}

/**
 * Element that holds the history lines. The refresh button stays outside it.
 *
 * @param {string|number} orderId
 * @returns {HTMLElement|null}
 */
function historyLinesElement(orderId)
{
	return document.getElementById("history-lines-" + orderId);
}

/**
 * Fetch and render one order's history.
 *
 * @param {string|number} orderId
 * @returns {void}
 */
function loadOrderHistory(orderId)
{
	const lines = historyLinesElement(orderId);
	const url = historyUrlFor(orderId);
	if (!lines || !url) {
		return;
	}

	lines.innerHTML = "";
	lines.insertAdjacentHTML(
		"beforeend",
		'<div class="d-flex justify-content-center mt-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>'
	);

	$.ajax({
		method: "GET",
		url: url,
		timeout: 10000,
		success: function (data) {
			renderOrderHistory(lines, data);
		},
		error: function (status) {
			lines.innerHTML = "";
			lines.append(document.createTextNode(status.statusText || "Error"));
		}
	});
}

/**
 * @param {HTMLElement} lines
 * @param {{changes: Array|string}} data
 * @returns {void}
 */
function renderOrderHistory(lines, data)
{
	lines.innerHTML = "";

	const changes = data && data.changes;
	if (!Array.isArray(changes) || changes.length === 0) {
		lines.append(document.createTextNode("Няма история"));
		return;
	}

	changes.forEach(function (row) {
		const fields = row.fields || {};
		if (fields.field_label === "дата") {
			return;
		}
		const dateObj = new Date(fields.date);
		const formattedDate = dateObj.toLocaleString("en-GB", {
			year: "numeric",
			month: "short",
			day: "2-digit",
			hour: "2-digit",
			minute: "2-digit",
		});
		const parts = [
			formattedDate + " —",
			fields.user,
			fields.operation,
			fields.related_item,
		];
		if (fields.field_label) {
			parts.push(fields.field_label);
		}
		if (fields.current_state && fields.new_state) {
			parts.push(fields.current_state + " --> " + fields.new_state);
		} else if (fields.current_state) {
			parts.push(fields.current_state);
		} else if (fields.new_state) {
			parts.push(fields.new_state);
		}
		const line = document.createElement("div");
		line.className = "history-line";
		line.append(document.createTextNode(parts.join(" ")));
		lines.append(line);
	});

	if (!lines.childNodes.length) {
		lines.append(document.createTextNode("Няма история"));
	}
}

/**
 * Bind history open and refresh once. Later calls are safe.
 *
 * @returns {void}
 */
function handle_orders_history()
{
	if (handle_orders_history.bound) {
		return;
	}
	handle_orders_history.bound = true;

	document.addEventListener("click", function (event) {
		const historyBtn = event.target.closest(".Historybtns");
		if (historyBtn) {
			loadOrderHistory(historyBtn.getAttribute("data-id"));
			return;
		}
		const refreshBtn = event.target.closest(".history-refresh-btn");
		if (refreshBtn) {
			loadOrderHistory(refreshBtn.getAttribute("data-history-refresh"));
		}
	});
}
