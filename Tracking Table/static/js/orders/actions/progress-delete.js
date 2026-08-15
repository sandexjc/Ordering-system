/*
 * orders/actions/progress-delete.js
 * ---------------------------------
 * Delegated handlers for progress-form Update and order Delete buttons (vanilla JS).
 * Delete POSTs same-origin with X-CSRFToken from the modal {% csrf_token %}.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Used by:
 *   - orders/actions/properties.js → handle_orders_properties
 *   - orders/actions/progress-step.js (apply_progress_update_response)
 */

/**
 * Sync a progress-bar step's active class and data-active flag.
 * Disabled steps never get `.active`, matching the server-rendered template
 * (`disabled` takes precedence so the inactive "x" stays visible).
 *
 * @param {string} elementId - DOM id of the step `<li>`.
 * @param {boolean} isActive - Whether the step should appear complete.
 * @returns {void}
 */
function sync_progress_step(elementId, isActive)
{
	const el = document.getElementById(elementId);
	if (!el) {
		return;
	}
	const showActive = isActive === true && !el.classList.contains("disabled");
	el.classList.toggle("active", showActive);
	el.classList.remove("is-error", "is-loading", "is-preview", "is-preview-off");
	el.removeAttribute("aria-busy");
	el.removeAttribute("aria-label");
	if (el.hasAttribute("data-active")) {
		el.dataset.active = isActive === true ? "1" : "0";
	}
}

/**
 * Enable or disable the vitrine "order taken" step from order_ready.
 * No-op on table details, which have no order_ready circle.
 *
 * @param {string|number} orderPk - Vitrine / order id.
 * @param {boolean} isReady - Whether order_ready is true.
 * @returns {void}
 */
function sync_vitrine_order_taken_enabled(orderPk, isReady)
{
	if (!document.getElementById("order-progress-order_ready-" + orderPk)) {
		return;
	}

	const taken = document.getElementById("order-progress-order_taken-" + orderPk);
	if (!taken) {
		return;
	}

	taken.classList.toggle("disabled", isReady !== true);
	if (isReady === true) {
		taken.setAttribute("role", "button");
		taken.setAttribute("tabindex", "0");
	} else {
		taken.removeAttribute("role");
		taken.removeAttribute("tabindex");
		taken.classList.remove("is-preview", "is-preview-off", "is-error");
	}
}

/**
 * Apply JSON from a progress update to list-row colors and progress bars.
 *
 * @param {object} data - Serialized `{ order, plates?, edges? }` payload.
 * @returns {void}
 */
function apply_progress_update_response(data)
{
	const payload = data || {};

	if (Array.isArray(payload.order)) {
		payload.order.forEach(o => {
			const row = document.getElementById(o.pk);

			if (row) {
				row.classList.toggle("orderTaken", o.fields.order_taken === true);
				row.classList.toggle("normalOrder", o.fields.order_taken !== true);
			}

			const idLabel = document.getElementById(`ID${o.pk}`);
			if (idLabel) {
				idLabel.style.color = o.fields.invoice ? "red" : "black";
			}

			sync_progress_step(`order-progress-order_taken-${o.pk}`, o.fields.order_taken === true);
			sync_progress_step(`order-progress-invoice-${o.pk}`, o.fields.invoice === true);
			sync_progress_step(`order-progress-order_ready-${o.pk}`, o.fields.order_ready === true);
			sync_vitrine_order_taken_enabled(o.pk, o.fields.order_ready === true);
		});
	}

	if (Array.isArray(payload.plates)) {
		payload.plates.forEach(p => {
			const plate = document.getElementById(`plate${p.pk}`);
			if (plate) {
				if (p.fields.ordered && !p.fields.from_client && !p.fields.delivered) {
					plate.style.color = "red";
				} else if (p.fields.delivered) {
					plate.style.color = "#8ac926";
				} else if (p.fields.from_client) {
					plate.style.color = "#7b2cbf";
				} else {
					plate.style.color = "black";
				}
			}

			["ordered", "delivered", "cutted", "edged"].forEach(state => {
				sync_progress_step(`plate-progress-${state}-${p.pk}`, p.fields[state] === true);
			});
		});
	}

	if (Array.isArray(payload.edges)) {
		payload.edges.forEach(e => {
			const edge = document.getElementById(`edge${e.pk}`);
			if (edge) {
				if (e.fields.ordered && !e.fields.delivered) {
					edge.style.color = "red";
				} else if (e.fields.delivered) {
					edge.style.color = "#8ac926";
				} else {
					edge.style.color = "black";
				}
			}

			["ordered", "delivered"].forEach(state => {
				sync_progress_step(`edge-progress-${state}-${e.pk}`, e.fields[state] === true);
			});
		});
	}

	if (typeof captureLiveRowsHtml === "function") {
		const root = document.getElementById("dynamic-orders-root");
		const viewName = root && root.getAttribute("data-current-view");
		if (viewName) {
			captureLiveRowsHtml(viewName);
		}
	}
}

/**
 * Run `callback` once after `el`'s `property` transition ends, or after `timeoutMs`.
 *
 * @param {HTMLElement|null} el - Element being animated.
 * @param {string} property - CSS property name to wait for.
 * @param {number} timeoutMs - Fallback if transitionend does not fire.
 * @param {function(): void} callback - Called once.
 * @returns {void}
 */
function after_css_transition(el, property, timeoutMs, callback)
{
	if (!el) {
		callback();
		return;
	}

	let finished = false;
	const finish = function () {
		if (finished) {
			return;
		}
		finished = true;
		el.removeEventListener("transitionend", onEnd);
		callback();
	};
	const onEnd = function (event) {
		if (event.target !== el || event.propertyName !== property) {
			return;
		}
		finish();
	};

	el.addEventListener("transitionend", onEnd);
	window.setTimeout(finish, timeoutMs);
}

/**
 * Drop a deleted order from the dynamic view cache and refresh the item counter.
 *
 * @param {string|number} id - Deleted order / vitrine id.
 * @returns {void}
 */
function sync_deleted_order_cache(id)
{
	const root = document.getElementById("dynamic-orders-root");
	const viewName = root && root.getAttribute("data-current-view");
	if (!viewName || !window.viewOrdersCache) {
		return;
	}

	const cacheEntry = viewOrdersCache.get(viewName);
	if (cacheEntry) {
		const key = String(id);
		if (cacheEntry.orderDetails) {
			delete cacheEntry.orderDetails[key];
		}
		if (Array.isArray(cacheEntry.openRowIds)) {
			cacheEntry.openRowIds = cacheEntry.openRowIds.filter(function (rowId) {
				return String(rowId) !== key;
			});
		}
		if (typeof cacheEntry.visibleItems === "number" && cacheEntry.visibleItems > 0) {
			cacheEntry.visibleItems -= 1;
		}
		viewOrdersCache.set(viewName, cacheEntry);
		if (typeof updateVisibleItemsCounter === "function") {
			updateVisibleItemsCounter(cacheEntry.visibleItems, viewName);
		}
	}

	if (typeof captureLiveRowsHtml === "function") {
		captureLiveRowsHtml(viewName);
	}
}

/**
 * Fade the list row, collapse its details, then remove related DOM and cache.
 *
 * @param {string|number} id - Deleted order / vitrine id.
 * @returns {void}
 */
function remove_deleted_order_row(id)
{
	const visibleRow = document.querySelector(`[data-row="${id}"]`);
	const hiddenRow = document.getElementById("hidden-row-" + id);
	const hiddenWrapper = hiddenRow ? hiddenRow.closest("tr") : null;
	const extras = [
		document.getElementById("delete-window-" + id),
		document.getElementById("progress-window-" + id),
		document.getElementById("offcanvas-history-tab-" + id)
	];

	const hiddenIsOpen = Boolean(
		hiddenRow
		&& !hiddenRow._isClosing
		&& (
			hiddenRow._isOpen === true
			|| hiddenRow.classList.contains("is-open")
			|| hiddenRow.style.display === "block"
		)
	);

	const removeAll = function () {
		visibleRow && visibleRow.remove();
		hiddenWrapper && hiddenWrapper.remove();
		if (hiddenRow && hiddenRow.isConnected) {
			hiddenRow.remove();
		}
		extras.forEach(function (el) {
			el && el.remove();
		});
		sync_deleted_order_cache(id);
	};

	let remaining = 1;
	if (hiddenIsOpen) {
		remaining += 1;
	}

	const markDone = function () {
		remaining -= 1;
		if (remaining <= 0) {
			removeAll();
		}
	};

	if (visibleRow) {
		void visibleRow.offsetHeight;
		visibleRow.classList.add("is-deleting");
		after_css_transition(visibleRow, "opacity", 250, markDone);
	} else {
		markDone();
	}

	if (hiddenIsOpen && typeof closeHiddenRow === "function") {
		closeHiddenRow(hiddenRow, visibleRow);
		after_css_transition(hiddenRow, "height", 400, markDone);
	} else if (hiddenIsOpen) {
		markDone();
	}
}

/**
 * Register (or re-register) document-level click handlers for `.btn-update` and `.btn-delete`.
 * Stores handlers on window.updateHandler / window.deleteHandler so they can be replaced safely.
 *
 * @returns {void}
 */
function setup_progress_delete_handlers()
{
	/**
	 * UPDATE (progress form) handler
	 * Works for table + vitrine
	 * Vanilla JS, delegated, app-agnostic
	 */

	/** Remove old handler if already registered */
	if (window.updateHandler) {
		document.removeEventListener("click", window.updateHandler);
	}

	/** Create a single delegated handler */
	window.updateHandler = function (event) {
		const btn = event.target.closest(".btn-update");
		if (!btn) return;

		event.preventDefault();

		const url = btn.dataset.url;
		const id = btn.dataset.id;

		const modal = btn.closest(".modal");
		if (!modal) return;

		const form = modal.querySelector("form");
		if (!form) return;

		/** Loading state */
		btn.disabled = true;
		const oldHtml = btn.innerHTML;
		btn.innerHTML = `Loading... <span class="spinner-border spinner-border-sm" role="status"></span>`;

		const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
		const formData = new FormData(form);

		fetch(url, {
			method: "POST",
			headers: { "X-CSRFToken": csrfToken },
			body: formData
		})
		.then(r => r.json().then(d => ({ ok: r.ok, data: d })))
		.then(result => {
			if (!result.ok) {
				throw new Error("Update failed");
			}

			/** Alerts */
			document.querySelectorAll(".ALERT-E-UPD-VIEW").forEach(el => el.style.display = "none");
			document.querySelectorAll(".ALERT-S-UPD-VIEW").forEach(el => el.style.display = "inline");

			/** Restore button */
			btn.disabled = false;
			btn.innerHTML = "Update";

			apply_progress_update_response(result.data);
			if (typeof rememberLocalOrderMutation === "function") {
				rememberLocalOrderMutation(id);
			}
		})
		.catch(err => {
			console.error(err);

			document.querySelectorAll(".ALERT-E-UPD-VIEW").forEach(el => el.style.display = "inline");
			document.querySelectorAll(".ALERT-S-UPD-VIEW").forEach(el => el.style.display = "none");

			btn.disabled = false;
			btn.innerHTML = oldHtml;
		});
	};

	/** Attach handler */
	document.addEventListener("click", window.updateHandler);


	/** Remove old window delete listener if already registered */
	if (window.deleteHandler) {
		document.removeEventListener("click", window.deleteHandler);
	}

	/** Create a single handler function and store it globally */
	window.deleteHandler = function(event) {
		const btn = event.target.closest(".btn-delete");
		if (!btn) return;

		event.preventDefault();

		const id = btn.dataset.id;
		const url = btn.dataset.url;
		const form = btn.closest("form");
		const csrfInput = form && form.querySelector("[name=csrfmiddlewaretoken]");
		const csrfToken = csrfInput && csrfInput.value;

		if (!url || !form || !csrfToken) {
			return;
		}

		/** UI loading state */
		btn.disabled = true;
		const oldHtml = btn.innerHTML;
		btn.innerHTML = `Loading... <span class="spinner-border spinner-border-sm"></span>`;

		const formData = new FormData(form);

		fetch(url, {
			method: "POST",
			credentials: "same-origin",
			headers: { "X-CSRFToken": csrfToken },
			body: formData
		})
		.then(r => r.json().then(d => ({ ok: r.ok, data: d })))
		.then(result => {
			if (!result.ok || result.data.status !== "ok") {
				throw new Error(result.data.message || "Deletion error");
			}

			/** Close modal */
			const modal = document.getElementById(`modal-delete-${id}`);
			if (modal) {
				const instance = bootstrap.Modal.getInstance(modal);
				if (instance) {
					instance.hide();
				}
			}

			remove_deleted_order_row(id);
			if (typeof rememberLocalOrderMutation === "function") {
				rememberLocalOrderMutation(id);
			}
		})
		.catch(err => {
			console.error(err);
			alert("Error deleting item. Please try again.");

			btn.disabled = false;
			btn.innerHTML = oldHtml;
		});
	};

	/** Attach the order delete handler */
	document.addEventListener("click", window.deleteHandler);
}
