/*
 * orders/actions/order-form-modal.js
 * ----------------------------------
 * Dynamic table create/edit order form modal: open, add-row, AJAX save,
 * 10s alerts, and live-list patch after success.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - bootstrap.bundle.js
 *   - dynamic/sync.js → rememberLocalOrderMutation, parseOrderRowPairs,
 *     applyRowPair, persistSyncedTbody, afterLiveSyncDomPatch,
 *     dropCachedOrderDetails, refreshOpenOrderDetailsIfNeeded
 *   - dynamic/fetch.js → getLiveOrdersBody
 *   - dynamic/filters.js → getFiltersForView
 *   - dynamic/cache.js → viewOrdersCache, captureLiveRowsHtml
 */

const ORDER_FORM_ALERT_MS = 10000;
const ORDER_FORM_TITLE_CREATE = "Нова заявка";
const ORDER_FORM_TITLE_EDIT = "Редактиране";

/**
 * True when the form URL is create (`/orderForm`), not edit (`/orderForm/<id>`).
 *
 * @param {string} url - Create or edit form URL.
 * @returns {boolean}
 */
function isOrderFormCreateUrl(url)
{
	if (!url) {
		return true;
	}
	try {
		const path = new URL(url, window.location.origin).pathname.replace(/\/+$/, "");
		return /\/orderForm$/.test(path);
	} catch (err) {
		return !/\/orderForm\/\d+/.test(String(url));
	}
}

/**
 * Loading markup shown in the modal body while the form fragment is fetched.
 *
 * @returns {string}
 */
function buildOrderFormLoadingHtml()
{
	return `
		<div class="text-center py-5">
			<div class="d-inline-flex align-items-center gap-2">
				<div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
				<span>Зареждане...</span>
			</div>
		</div>
	`;
}

/**
 * Error + retry markup shown when the form fragment fails to load.
 *
 * @returns {string}
 */
function buildOrderFormLoadErrorHtml()
{
	return `
		<div class="text-center py-5">
			<h6 class="text-danger mb-3">Възникна грешка при зареждане на формата</h6>
			<button type="button" class="btn btn-sm btn-outline-primary" data-order-form-retry>
				Опитай отново
			</button>
		</div>
	`;
}

/**
 * Hide a modal alert and clear its dismiss timer.
 *
 * @param {HTMLElement|null} alertEl - Alert wrapper.
 * @returns {void}
 */
function hideOrderFormAlert(alertEl)
{
	if (!alertEl) {
		return;
	}
	if (alertEl._dismissTimeout) {
		window.clearTimeout(alertEl._dismissTimeout);
		alertEl._dismissTimeout = null;
	}
	alertEl.style.display = "none";
}

/**
 * Show a modal alert for 10s. Optional message replaces the default text.
 *
 * @param {HTMLElement|null} alertEl - Alert wrapper.
 * @param {string} [message] - Optional message text.
 * @returns {void}
 */
function showOrderFormAlert(alertEl, message)
{
	if (!alertEl) {
		return;
	}
	const msgEl = alertEl.querySelector(".alertmsgdiv");
	if (msgEl && message) {
		msgEl.textContent = message;
	}
	if (alertEl._dismissTimeout) {
		window.clearTimeout(alertEl._dismissTimeout);
	}
	alertEl.style.display = "block";
	alertEl._dismissTimeout = window.setTimeout(function () {
		alertEl.style.display = "none";
		alertEl._dismissTimeout = null;
	}, ORDER_FORM_ALERT_MS);
}

/**
 * Modal root and its success/fail alert nodes.
 *
 * @returns {{modal: HTMLElement|null, body: HTMLElement|null, title: HTMLElement|null, successAlert: HTMLElement|null, errorAlert: HTMLElement|null}}
 */
function getOrderFormModalParts()
{
	const modal = document.getElementById("order-form-modal");
	return {
		modal: modal,
		body: document.getElementById("order-form-modal-body"),
		title: document.getElementById("order-form-modal-title"),
		successAlert: modal && modal.querySelector(".ALERT-S-ORD-VIEW"),
		errorAlert: modal && modal.querySelector(".ALERT-E-ORD-VIEW"),
	};
}

/**
 * Copy the fragment's data-modal-title onto the Bootstrap header.
 *
 * @param {HTMLElement|null} form - Fetched form element.
 * @param {HTMLElement|null} titleEl - Modal title node.
 * @returns {void}
 */
function syncOrderFormModalTitle(form, titleEl)
{
	if (!form || !titleEl) {
		return;
	}
	const nextTitle = form.getAttribute("data-modal-title");
	if (nextTitle) {
		titleEl.textContent = nextTitle;
	}
}

/**
 * Replace modal body HTML and sync the header title from the new form.
 *
 * @param {string} html - Form fragment HTML.
 * @returns {void}
 */
function setOrderFormModalBody(html)
{
	const parts = getOrderFormModalParts();
	if (!parts.body) {
		return;
	}
	parts.body.innerHTML = html || "";
	syncOrderFormModalTitle(parts.body.querySelector("#order-form-modal-form"), parts.title);
}

/**
 * Clone a formset empty_form row and bump TOTAL_FORMS.
 *
 * @param {HTMLElement} formsetRoot - Wrapper with data-formset-prefix.
 * @returns {void}
 */
function addOrderFormsetRow(formsetRoot)
{
	if (!formsetRoot) {
		return;
	}
	const prefix = formsetRoot.getAttribute("data-formset-prefix");
	const template = formsetRoot.querySelector("[data-formset-empty]");
	const tbody = formsetRoot.querySelector("[data-formset-body]");
	const form = formsetRoot.closest("form");
	const totalInput = form && prefix
		? form.querySelector('[name="' + prefix + '-TOTAL_FORMS"]')
		: null;
	if (!prefix || !template || !tbody || !totalInput) {
		return;
	}

	const index = Number.parseInt(totalInput.value, 10) || 0;
	const holder = document.createElement("tbody");
	holder.innerHTML = template.innerHTML.replace(/__prefix__/g, String(index)).trim();
	const row = holder.querySelector("tr");
	if (!row) {
		return;
	}

	const addRow = tbody.querySelector(".order-form-add-row");
	const totals = tbody.querySelector(".order-form-totals-row");
	const insertBefore = addRow || totals;
	if (insertBefore) {
		tbody.insertBefore(row, insertBefore);
	} else {
		tbody.appendChild(row);
	}
	totalInput.value = String(index + 1);
}

/**
 * True when a formset row has a saved instance id.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {boolean}
 */
function isSavedOrderFormRow(row)
{
	const idInput = row.querySelector('input[type="hidden"][name$="-id"]');
	return Boolean(idInput && String(idInput.value || "").trim());
}

/**
 * True when the row has no user-entered item data.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {boolean}
 */
function isEmptyOrderFormRow(row)
{
	const fields = row.querySelectorAll("input, select, textarea");
	for (let index = 0; index < fields.length; index += 1) {
		const el = fields[index];
		const name = el.name || "";
		if (!name || el.type === "hidden" || el.readOnly || el.disabled || name.endsWith("-id") || name.endsWith("-DELETE")) {
			continue;
		}
		if (el.type === "checkbox") {
			if (name.endsWith("-from_client") && el.checked) {
				return false;
			}
			continue;
		}
		if (el.tagName === "SELECT") {
			continue;
		}
		const value = String(el.value || "").trim();
		if (value !== "" && value !== "0" && value !== "0.0" && value !== "0.00") {
			return false;
		}
	}
	return true;
}

/**
 * Reindex remaining item rows and TOTAL_FORMS for one formset.
 *
 * @param {HTMLElement} formsetRoot - Wrapper with data-formset-prefix.
 * @returns {void}
 */
function reindexOrderFormsetRows(formsetRoot)
{
	const prefix = formsetRoot.getAttribute("data-formset-prefix");
	const tbody = formsetRoot.querySelector("[data-formset-body]");
	const form = formsetRoot.closest("form");
	const totalInput = form && prefix
		? form.querySelector('[name="' + prefix + '-TOTAL_FORMS"]')
		: null;
	if (!prefix || !tbody || !totalInput) {
		return;
	}

	const rows = tbody.querySelectorAll("tr.order-form-item-row");
	const pattern = new RegExp(prefix.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "-\\d+");
	rows.forEach(function (row, index) {
		const nextPrefix = prefix + "-" + String(index);
		row.querySelectorAll("[name], [id], [for]").forEach(function (el) {
			["name", "id", "for"].forEach(function (attr) {
				const value = el.getAttribute(attr);
				if (!value || !pattern.test(value)) {
					return;
				}
				el.setAttribute(attr, value.replace(pattern, nextPrefix));
			});
		});
	});
	totalInput.value = String(rows.length);
}

/**
 * Swap trash / restore icon on a row action button.
 *
 * @param {HTMLElement} row - Item row.
 * @param {boolean} pendingDelete - Whether the row is marked for deletion.
 * @returns {void}
 */
function syncOrderFormRowAction(row, pendingDelete)
{
	const btn = row.querySelector("[data-order-form-row-action]");
	if (!btn) {
		return;
	}
	const img = btn.querySelector("img");
	const src = pendingDelete ? btn.dataset.restoreSrc : btn.dataset.deleteSrc;
	const label = pendingDelete ? "Възстанови" : "Изтрий";
	if (img && src) {
		img.src = src;
	}
	btn.setAttribute("title", label);
	btn.setAttribute("aria-label", label);
}

/**
 * Mark a saved/filled row for deletion on save, or unmark it.
 *
 * @param {HTMLElement} row - Item row.
 * @param {boolean} pendingDelete - Whether to mark for deletion.
 * @returns {void}
 */
function setOrderFormRowPendingDelete(row, pendingDelete)
{
	row.classList.toggle("is-pending-delete", pendingDelete);
	const deleteInput = row.querySelector('input[name$="-DELETE"]');
	if (deleteInput) {
		deleteInput.checked = pendingDelete;
	}
	syncOrderFormRowAction(row, pendingDelete);
}

/**
 * Handle trash / restore click on a formset item row.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {void}
 */
function handleOrderFormRowAction(row)
{
	if (row.classList.contains("is-pending-delete")) {
		setOrderFormRowPendingDelete(row, false);
		return;
	}

	const saved = isSavedOrderFormRow(row);
	if (!saved && isEmptyOrderFormRow(row)) {
		const formsetRoot = row.closest("[data-formset]");
		row.remove();
		if (formsetRoot) {
			reindexOrderFormsetRows(formsetRoot);
		}
		return;
	}

	setOrderFormRowPendingDelete(row, true);
}

/**
 * Copy live field values onto a cloned form (cloneNode does not).
 *
 * @param {HTMLFormElement} form - Visible modal form.
 * @returns {HTMLFormElement} Detached clone with current values.
 */
function cloneOrderFormWithValues(form)
{
	const clone = form.cloneNode(true);
	const source = form.elements;
	const target = clone.elements;
	for (let index = 0; index < source.length; index += 1) {
		const fromEl = source[index];
		const toEl = target[index];
		if (!fromEl || !toEl) {
			continue;
		}
		if (fromEl.type === "checkbox" || fromEl.type === "radio") {
			toEl.checked = fromEl.checked;
		} else if (fromEl.tagName === "SELECT") {
			toEl.selectedIndex = fromEl.selectedIndex;
		} else {
			toEl.value = fromEl.value;
		}
	}
	return clone;
}

/**
 * Drop faded extra rows that have no DELETE field, then reindex.
 *
 * @param {HTMLFormElement} form - Modal order form.
 * @returns {void}
 */
function prepareOrderFormsetsForSubmit(form)
{
	form.querySelectorAll("[data-formset]").forEach(function (formsetRoot) {
		const tbody = formsetRoot.querySelector("[data-formset-body]");
		if (!tbody) {
			return;
		}
		tbody.querySelectorAll("tr.order-form-item-row.is-pending-delete").forEach(function (row) {
			const deleteInput = row.querySelector('input[name$="-DELETE"]');
			if (deleteInput) {
				deleteInput.checked = true;
				return;
			}
			row.remove();
		});
		reindexOrderFormsetRows(formsetRoot);
	});
}

/**
 * Patch the live table row from the save response and refresh open details.
 *
 * @param {string|number} orderId - Saved order id.
 * @param {string} rowsHtml - Summary + hidden row pair HTML.
 * @returns {void}
 */
function applyOrderFormLiveRow(orderId, rowsHtml)
{
	const viewName = "table";
	if (typeof rememberLocalOrderMutation === "function") {
		rememberLocalOrderMutation(orderId);
	}

	const tbody = typeof getLiveOrdersBody === "function"
		? getLiveOrdersBody(viewName)
		: null;
	if (!tbody || typeof parseOrderRowPairs !== "function" || typeof applyRowPair !== "function") {
		return;
	}

	const pairs = parseOrderRowPairs(rowsHtml || "");
	const pair = pairs.length ? pairs[0] : null;
	if (!pair || !pair.id) {
		return;
	}

	const filters = typeof getFiltersForView === "function"
		? getFiltersForView(viewName)
		: { sortBy: "date", sortDir: "desc" };
	const cacheEntry = typeof viewOrdersCache !== "undefined"
		? viewOrdersCache.get(viewName)
		: null;
	const hasMore = Boolean(cacheEntry && cacheEntry.hasMore);

	applyRowPair(viewName, tbody, pair, true, hasMore, filters);
	if (typeof rememberLocalOrderMutation === "function") {
		rememberLocalOrderMutation(orderId);
	}
	if (typeof persistSyncedTbody === "function") {
		persistSyncedTbody(viewName, tbody, true);
	}
	if (typeof afterLiveSyncDomPatch === "function") {
		afterLiveSyncDomPatch(viewName);
	}
	if (typeof captureLiveRowsHtml === "function") {
		captureLiveRowsHtml(viewName);
	}
	if (typeof dropCachedOrderDetails === "function") {
		dropCachedOrderDetails(viewName, orderId);
	}
	if (typeof refreshOpenOrderDetailsIfNeeded === "function") {
		refreshOpenOrderDetailsIfNeeded(orderId);
	}
}

/**
 * GET the form fragment and show it in the already-open modal.
 *
 * @param {string} url - Create or edit form URL.
 * @returns {void}
 */
function loadOrderFormIntoModal(url)
{
	const parts = getOrderFormModalParts();
	if (!parts.body || !url) {
		return;
	}

	if (parts.modal) {
		parts.modal.dataset.orderFormUrl = url;
	}

	hideOrderFormAlert(parts.successAlert);
	hideOrderFormAlert(parts.errorAlert);
	parts.body.innerHTML = buildOrderFormLoadingHtml();

	fetch(url, {
		method: "GET",
		credentials: "same-origin",
		headers: { "X-Requested-With": "XMLHttpRequest" }
	})
		.then(function (response) {
			if (!response.ok) {
				throw new Error("Form load failed");
			}
			return response.text();
		})
		.then(function (html) {
			setOrderFormModalBody(html);
		})
		.catch(function (err) {
			console.error(err);
			parts.body.innerHTML = buildOrderFormLoadErrorHtml();
		});
}

/**
 * Open the modal and fetch the empty (create) or populated (edit) form.
 *
 * @param {string} url - Create or edit form URL.
 * @returns {void}
 */
function openOrderFormModal(url)
{
	if (!url) {
		return;
	}
	const parts = getOrderFormModalParts();
	if (!parts.modal) {
		return;
	}

	if (parts.title) {
		parts.title.textContent = isOrderFormCreateUrl(url)
			? ORDER_FORM_TITLE_CREATE
			: ORDER_FORM_TITLE_EDIT;
	}
	hideOrderFormAlert(parts.successAlert);
	hideOrderFormAlert(parts.errorAlert);
	if (parts.body) {
		parts.body.innerHTML = buildOrderFormLoadingHtml();
	}

	const instance = bootstrap.Modal.getOrCreateInstance(parts.modal, {
		backdrop: "static",
		keyboard: false
	});
	instance.show();
	loadOrderFormIntoModal(url);
}

/**
 * POST the modal form. Create stays open as edit; edit closes on success.
 *
 * @param {HTMLFormElement} form - Modal order form.
 * @returns {void}
 */
function submitOrderFormModal(form)
{
	const parts = getOrderFormModalParts();
	const url = form.getAttribute("action");
	const saveBtn = form.querySelector("#order-form-modal-save");
	const csrfInput = form.querySelector("[name=csrfmiddlewaretoken]");
	if (!url || !csrfInput) {
		return;
	}

	hideOrderFormAlert(parts.successAlert);
	hideOrderFormAlert(parts.errorAlert);

	const wasCreate = !form.getAttribute("data-order-id");
	const submitForm = cloneOrderFormWithValues(form);
	prepareOrderFormsetsForSubmit(submitForm);

	let oldHtml = "";
	if (saveBtn) {
		saveBtn.disabled = true;
		oldHtml = saveBtn.innerHTML;
		saveBtn.innerHTML = 'Loading... <span class="spinner-border spinner-border-sm" role="status"></span>';
	}

	const controller = new AbortController();
	const timeoutId = window.setTimeout(function () {
		controller.abort();
	}, 10000);

	fetch(url, {
		method: "POST",
		credentials: "same-origin",
		headers: { "X-CSRFToken": csrfInput.value, "X-Requested-With": "XMLHttpRequest" },
		body: new FormData(submitForm),
		signal: controller.signal
	})
		.then(function (response) {
			return response.json().then(function (data) {
				return { ok: response.ok, status: response.status, data: data };
			});
		})
		.then(function (result) {
			window.clearTimeout(timeoutId);
			const data = result.data || {};
			if (!result.ok || data.status !== "ok") {
				const error = new Error(data.message || "Save failed");
				error.userMessage = data.message;
				error.formHtml = data.form_html;
				throw error;
			}

			if (data.id != null && data.rows_html) {
				applyOrderFormLiveRow(data.id, data.rows_html);
			}
			if (wasCreate) {
				if (data.form_html) {
					setOrderFormModalBody(data.form_html);
				}
			} else if (parts.modal) {
				const instance = bootstrap.Modal.getInstance(parts.modal);
				if (instance) {
					instance.hide();
				}
			}
		})
		.catch(function (err) {
			window.clearTimeout(timeoutId);
			console.error(err);
			if (err && err.formHtml) {
				setOrderFormModalBody(err.formHtml);
			} else if (saveBtn) {
				saveBtn.disabled = false;
				saveBtn.innerHTML = oldHtml;
			}
			showOrderFormAlert(
				parts.errorAlert,
				(err && err.userMessage) || "Възникна грешка!"
			);
		});
}

/**
 * Bind create/edit intercepts, add-row, submit, and alert dismiss.
 *
 * @returns {void}
 */
function setupOrderFormModal()
{
	const parts = getOrderFormModalParts();
	if (!parts.modal) {
		return;
	}

	document.addEventListener("click", function (event) {
		const addLink = event.target.closest("#dynamic-new-order-link");
		if (addLink) {
			const root = document.getElementById("dynamic-orders-root");
			if (!root || root.dataset.currentView !== "table") {
				return;
			}
			event.preventDefault();
			openOrderFormModal(addLink.dataset.tableFormUrl);
			return;
		}

		const editBtn = event.target.closest(".btn-order-form-modal");
		if (editBtn) {
			event.preventDefault();
			openOrderFormModal(editBtn.dataset.orderFormUrl);
		}
	});

	parts.modal.addEventListener("click", function (event) {
		const retryBtn = event.target.closest("[data-order-form-retry]");
		if (retryBtn) {
			event.preventDefault();
			loadOrderFormIntoModal(parts.modal.dataset.orderFormUrl);
			return;
		}

		const rowActionBtn = event.target.closest("[data-order-form-row-action]");
		if (rowActionBtn) {
			event.preventDefault();
			const row = rowActionBtn.closest("tr.order-form-item-row");
			if (row) {
				handleOrderFormRowAction(row);
			}
			return;
		}

		const addRowBtn = event.target.closest("[data-add-formset-row]");
		if (addRowBtn) {
			event.preventDefault();
			addOrderFormsetRow(addRowBtn.closest("[data-formset]"));
			return;
		}

		const closeBtn = event.target.closest(".ALERT-S-ORD-VIEW .btn-close, .ALERT-E-ORD-VIEW .btn-close");
		if (closeBtn) {
			event.preventDefault();
			hideOrderFormAlert(closeBtn.closest(".ALERT-S-ORD-VIEW, .ALERT-E-ORD-VIEW"));
		}
	});

	parts.modal.addEventListener("submit", function (event) {
		const form = event.target.closest("#order-form-modal-form");
		if (!form) {
			return;
		}
		event.preventDefault();
		submitOrderFormModal(form);
	});

	parts.modal.addEventListener("hidden.bs.modal", function () {
		hideOrderFormAlert(parts.successAlert);
		hideOrderFormAlert(parts.errorAlert);
		if (parts.body) {
			parts.body.innerHTML = "";
		}
		if (parts.title) {
			parts.title.textContent = ORDER_FORM_TITLE_CREATE;
		}
		delete parts.modal.dataset.orderFormUrl;
	});
}

document.addEventListener("DOMContentLoaded", function () {
	setupOrderFormModal();
});
