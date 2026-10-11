/*
 * orders/actions/order-form-modal.js
 * ----------------------------------
 * Dynamic table/vitrine create/edit order form modal: open, add-row, AJAX save,
 * unsaved-row highlight, save toasts, live-list patch after success, and
 * merge of a remote order update into an already-open edit form.
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

const ORDER_FORM_TOAST_SUCCESS_MS = 2000;
const ORDER_FORM_TOAST_ERROR_MS = 10000;
const ORDER_FORM_TITLE_CREATE = "Нова заявка";
const ORDER_FORM_TITLE_EDIT = "Редактиране";
const ORDER_FORM_REMOTE_UPDATE_MESSAGE = "Поръчката е обновена от друг потребител.";
let activeOrderFormToast = null;
let allowOrderFormClose = false;
let orderFormSubmitInFlight = false;
let orderFormRemoteSyncInFlight = false;
let orderFormRemoteSyncQueued = false;
let orderFormRemoteSyncToken = 0;

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
 * Normalize a decimal-looking value the same way price settings does,
 * so "10", "10.0", and "10,00" compare as one saved value.
 *
 * @param {string} value - Raw field text.
 * @returns {string}
 */
function normalizeOrderFormDecimal(value)
{
	const cleaned = String(value ?? "").trim().replace(",", ".");
	if (cleaned === "") {
		return "";
	}
	const numeric = Number(cleaned);
	return Number.isFinite(numeric) ? numeric.toFixed(2) : cleaned;
}

/**
 * Comparable snapshot of one control.
 *
 * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} el - Form control.
 * @returns {string}
 */
function normalizeOrderFormValue(el)
{
	if (el.type === "checkbox" || el.type === "radio") {
		return el.checked ? "1" : "0";
	}
	const raw = String(el.value ?? "").trim();
	if (/^-?\d+([.,]\d+)?$/.test(raw)) {
		return normalizeOrderFormDecimal(raw);
	}
	return raw;
}

/**
 * True for controls whose edits should highlight a row.
 *
 * @param {HTMLElement} el - Candidate control.
 * @returns {boolean}
 */
function isTrackableOrderFormField(el)
{
	const name = el.name || "";
	if (!name || el.disabled || el.readOnly) {
		return false;
	}
	if (el.type === "hidden" || el.type === "button" || el.type === "submit" || el.type === "file") {
		return false;
	}
	if (name === "csrfmiddlewaretoken" || name === "manual-seal-mode") {
		return false;
	}
	if (
		name.endsWith("-TOTAL_FORMS")
		|| name.endsWith("-INITIAL_FORMS")
		|| name.endsWith("-MIN_NUM_FORMS")
		|| name.endsWith("-MAX_NUM_FORMS")
		|| name.endsWith("-id")
	) {
		return false;
	}
	return true;
}

/**
 * Remember the loaded value of each tracked control under `root`.
 *
 * @param {ParentNode} root - Form or a newly added row.
 * @returns {void}
 */
function snapshotOrderFormInitials(root)
{
	if (!root) {
		return;
	}
	root.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!isTrackableOrderFormField(el)) {
			return;
		}
		el.dataset.initialValue = normalizeOrderFormValue(el);
	});
}

/**
 * Name → saved value map from a form that is about to be posted.
 * Used to restore highlights when the server re-renders the form on error.
 *
 * @param {ParentNode} root - Form clone after submit preparation.
 * @returns {Object<string, string>}
 */
function collectOrderFormInitials(root)
{
	const initials = {};
	if (!root) {
		return initials;
	}
	root.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!isTrackableOrderFormField(el) || !el.name) {
			return;
		}
		initials[el.name] = el.dataset.initialValue != null
			? el.dataset.initialValue
			: normalizeOrderFormValue(el);
	});
	return initials;
}

/**
 * Put saved baselines back onto a re-rendered form, then refresh highlights.
 *
 * @param {ParentNode} root - Replacement form.
 * @param {Object<string, string>} initials - Baselines keyed by field name.
 * @returns {void}
 */
function applyOrderFormInitials(root, initials)
{
	if (!root) {
		return;
	}
	const saved = initials || {};
	root.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!isTrackableOrderFormField(el)) {
			return;
		}
		if (Object.prototype.hasOwnProperty.call(saved, el.name)) {
			el.dataset.initialValue = saved[el.name];
			return;
		}
		el.dataset.initialValue = normalizeOrderFormValue(el);
	});
	updateOrderFormDirtyState(root.closest("form") || root);
}

/**
 * Highlight unsaved edits.
 * Table lines highlight the whole row. Main-form fields highlight only the control, not its label.
 *
 * @param {ParentNode|null} form - Modal order form.
 * @returns {void}
 */
function updateOrderFormDirtyState(form)
{
	if (!form) {
		return;
	}
	const dirtyRows = new Set();
	form.querySelectorAll("input, select, textarea").forEach(function (el) {
		const row = el.closest("tr");
		const changed = isTrackableOrderFormField(el)
			&& el.dataset.initialValue != null
			&& normalizeOrderFormValue(el) !== el.dataset.initialValue;
		if (row) {
			el.classList.remove("is-dirty");
			if (changed) {
				dirtyRows.add(row);
			}
			return;
		}
		el.classList.toggle("is-dirty", changed);
	});
	form.querySelectorAll("tr.is-dirty").forEach(function (row) {
		if (!dirtyRows.has(row)) {
			row.classList.remove("is-dirty");
		}
	});
	dirtyRows.forEach(function (row) {
		row.classList.add("is-dirty");
	});
}

/**
 * True when a highlighted row or main-form field still differs from the saved values.
 *
 * @returns {boolean}
 */
function orderFormHasUnsavedChanges()
{
	const form = document.getElementById("order-form-modal-form");
	return Boolean(form && form.querySelector(".is-dirty"));
}

/**
 * Confirmation shown over the order form when close would drop unsaved edits.
 *
 * @returns {HTMLElement|null}
 */
function orderFormUnsavedDialog()
{
	return document.getElementById("order-form-unsaved-modal");
}

/**
 * Hide the unsaved-changes confirmation.
 *
 * @returns {void}
 */
function hideOrderFormUnsavedDialog()
{
	const dialog = orderFormUnsavedDialog();
	if (!dialog) {
		return;
	}
	const focused = document.activeElement;
	if (focused instanceof HTMLElement && dialog.contains(focused)) {
		focused.blur();
	}
	dialog.classList.remove("is-open");
	dialog.setAttribute("aria-hidden", "true");
}

/**
 * Show the unsaved-changes confirmation.
 *
 * @returns {void}
 */
function showOrderFormUnsavedDialog()
{
	const dialog = orderFormUnsavedDialog();
	if (!dialog) {
		return;
	}
	dialog.setAttribute("aria-hidden", "false");
	window.requestAnimationFrame(function () {
		dialog.classList.add("is-open");
	});
	const cancelBtn = dialog.querySelector(".modal-footer [data-order-form-unsaved-cancel]");
	if (cancelBtn) {
		cancelBtn.focus();
	}
}

/**
 * Move focus out of the modal before Bootstrap marks it aria-hidden.
 *
 * @param {HTMLElement|null} modal - Order form modal.
 * @returns {void}
 */
function releaseOrderFormModalFocus(modal)
{
	if (!modal) {
		return;
	}
	const focused = document.activeElement;
	if (focused instanceof HTMLElement && modal.contains(focused)) {
		focused.blur();
	}
	modal.inert = true;
}

/**
 * Close the order form without asking again.
 *
 * @returns {void}
 */
function closeOrderFormModal()
{
	const parts = getOrderFormModalParts();
	if (!parts.modal || typeof bootstrap === "undefined") {
		return;
	}
	allowOrderFormClose = true;
	hideOrderFormUnsavedDialog();
	const instance = bootstrap.Modal.getInstance(parts.modal) || bootstrap.Modal.getOrCreateInstance(parts.modal);
	instance.hide();
}

/**
 * Success text, including the saved order number when the server returned one.
 *
 * @param {string|number|null|undefined} orderId - Saved order id.
 * @returns {string}
 */
function orderFormSuccessMessage(orderId)
{
	if (orderId == null || String(orderId).trim() === "") {
		return "Промените са запазени успешно.";
	}
	return "Промените по поръчка №" + String(orderId) + " са запазени успешно.";
}

/**
 * Success toast hides after 2s. Error toast stays longer and can be closed.
 *
 * @param {string} message - Toast text.
 * @param {"success"|"error"} type - Visual variant.
 * @returns {void}
 */
function showOrderFormToast(message, type)
{
	const toastEl = document.getElementById("order-form-toast");
	const toastBody = document.getElementById("order-form-toast-body");
	if (!toastEl || !toastBody || typeof bootstrap === "undefined" || !bootstrap.Toast) {
		return;
	}

	const existing = bootstrap.Toast.getInstance(toastEl);
	if (existing) {
		existing.dispose();
	}
	activeOrderFormToast = null;

	const delay = type === "success" ? ORDER_FORM_TOAST_SUCCESS_MS : ORDER_FORM_TOAST_ERROR_MS;
	toastEl.classList.remove("bg-success", "bg-danger");
	toastEl.classList.add(type === "success" ? "bg-success" : "bg-danger");
	toastBody.textContent = message;
	activeOrderFormToast = new bootstrap.Toast(toastEl, { delay: delay, autohide: true });
	activeOrderFormToast.show();
}

/**
 * Modal root nodes.
 *
 * @returns {{modal: HTMLElement|null, body: HTMLElement|null, title: HTMLElement|null}}
 */
function getOrderFormModalParts()
{
	return {
		modal: document.getElementById("order-form-modal"),
		body: document.getElementById("order-form-modal-body"),
		title: document.getElementById("order-form-modal-title"),
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
 * @param {{initials?: Object<string, string>}} [options] - When `initials` is set, keep
 *   unsaved highlights against that baseline (failed save). Otherwise snapshot the new form.
 * @returns {void}
 */
function setOrderFormModalBody(html, options)
{
	const parts = getOrderFormModalParts();
	if (!parts.body) {
		return;
	}
	parts.body.innerHTML = html || "";
	const form = parts.body.querySelector("#order-form-modal-form");
	syncOrderFormModalTitle(form, parts.title);
	if (form) {
		if (options && options.initials) {
			applyOrderFormInitials(form, options.initials);
		} else {
			snapshotOrderFormInitials(form);
			updateOrderFormDirtyState(form);
		}
	}
	if (typeof setupManualSealToggle === "function") {
		setupManualSealToggle(parts.body);
	}
	flushQueuedOrderFormRemoteSync();
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
	row.setAttribute("data-user-added", "1");
	snapshotOrderFormInitials(row);
}

/**
 * True when a formset row has a saved instance id, or a DELETE field
 * (initial/saved forms; extra empty rows omit DELETE).
 *
 * @param {HTMLElement} row - Item row.
 * @returns {boolean}
 */
function isSavedOrderFormRow(row)
{
	const idInput = row.querySelector('input[type="hidden"][name$="-id"]');
	if (idInput && String(idInput.value || "").trim()) {
		return true;
	}
	return Boolean(row.querySelector('input[name$="-DELETE"]'));
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
			if (el.selectedIndex > 0) {
				return false;
			}
			continue;
		}
		const value = String(el.value || "").trim();
		if (name.endsWith("-quantity") && row.querySelector('input[name$="-length"]')) {
			if (value === "" || value === "0" || value === "1") {
				continue;
			}
			return false;
		}
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
	updateOrderFormDirtyState(row.closest("form"));
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

	if (!isSavedOrderFormRow(row)) {
		const formsetRoot = row.closest("[data-formset]");
		const form = row.closest("form");
		row.remove();
		if (formsetRoot) {
			reindexOrderFormsetRows(formsetRoot);
			syncOrderFormsetInitialCount(formsetRoot);
		}
		updateOrderFormDirtyState(form);
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
	const root = document.getElementById("dynamic-orders-root");
	const viewName = root && root.dataset.currentView ? root.dataset.currentView : "table";
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

	/*
	 * Force replace: rememberLocalOrderMutation stamps Date.now() on the live row,
     * which is newer than the server updated_at and would otherwise skip the patch.
	 */
    applyRowPair(viewName, tbody, pair, true, hasMore, filters, true);

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
 * Saved instance id on a formset row, or "" for an extra row.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {string}
 */
function orderFormRowInstanceId(row)
{
	const idInput = row.querySelector('input[name$="-id"]');
	if (!idInput) {
		return "";
	}
	return String(idInput.value || "").trim();
}

/**
 * Field name without the formset index (`plates-0-material` → `material`).
 *
 * @param {string} name - Control name.
 * @returns {string}
 */
function orderFormFieldKey(name)
{
	return String(name || "").replace(/^.*-\d+-/, "");
}

/**
 * True when one control differs from the value it was loaded or last synced with.
 *
 * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} el - Form control.
 * @returns {boolean}
 */
function isOrderFormControlDirty(el)
{
	return isTrackableOrderFormField(el)
		&& el.dataset.initialValue != null
		&& normalizeOrderFormValue(el) !== el.dataset.initialValue;
}

/**
 * True when the row still has edits the user has not saved.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {boolean}
 */
function orderFormRowHasUnsavedChanges(row)
{
	if (row.classList.contains("is-pending-delete") || row.classList.contains("is-dirty")) {
		return true;
	}
	const fields = row.querySelectorAll("input, select, textarea");
	for (let index = 0; index < fields.length; index += 1) {
		if (isOrderFormControlDirty(fields[index])) {
			return true;
		}
	}
	return false;
}

/**
 * Extra blank row from the server, not a row the user added or edited.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {boolean}
 */
function isBlankExtraOrderFormRow(row)
{
	if (row.getAttribute("data-user-added") === "1") {
		return false;
	}
	if (row.classList.contains("is-pending-delete")) {
		return false;
	}
	if (orderFormRowInstanceId(row)) {
		return false;
	}
	return !orderFormRowHasUnsavedChanges(row);
}

/**
 * Copy the current value of one control onto another.
 *
 * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} fromEl - Source control.
 * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} toEl - Target control.
 * @returns {void}
 */
function copyOrderFormControlValue(fromEl, toEl)
{
	if (fromEl.type === "checkbox" || fromEl.type === "radio") {
		toEl.checked = fromEl.checked;
		return;
	}
	if (fromEl.tagName === "SELECT") {
		toEl.value = fromEl.value;
		return;
	}
	toEl.value = fromEl.value;
}

/**
 * Comparable field list for one item row, ignoring the formset index.
 *
 * @param {HTMLElement} row - Item row.
 * @returns {string}
 */
function orderFormRowSignature(row)
{
	return Array.from(row.querySelectorAll("input, select, textarea"))
		.filter(function (el) {
			return el.name && el.type !== "hidden";
		})
		.map(function (el) {
			return orderFormFieldKey(el.name) + "=" + normalizeOrderFormValue(el);
		})
		.join("|");
}

/**
 * Match key for a control. Radios that share a name stay distinct.
 *
 * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} el - Form control.
 * @returns {string}
 */
function orderFormControlMatchKey(el)
{
	if (el.type === "radio") {
		return el.name + "::" + el.value;
	}
	return el.name;
}

/**
 * Light-green highlight for a row or header field brought in by a remote update.
 * Clears when the user focuses it, or after the same delay as the table highlight.
 *
 * @param {HTMLElement} el - Row or control.
 * @returns {void}
 */
function armOrderFormSyncHighlight(el)
{
	if (!el) {
		return;
	}
	el.classList.add("is-sync-fresh");
	if (el._orderFormSyncTimer) {
		window.clearTimeout(el._orderFormSyncTimer);
	}
	const waitMs = typeof SYNC_HIGHLIGHT_MS === "number" ? SYNC_HIGHLIGHT_MS : 120000;
	el._orderFormSyncTimer = window.setTimeout(function () {
		el._orderFormSyncTimer = null;
		clearOrderFormSyncHighlight(el);
	}, waitMs);
}

/**
 * Remove the remote-update green from a row or header field.
 *
 * @param {HTMLElement|null} el - Row or control.
 * @returns {void}
 */
function clearOrderFormSyncHighlight(el)
{
	if (!el) {
		return;
	}
	if (el._orderFormSyncTimer) {
		window.clearTimeout(el._orderFormSyncTimer);
		el._orderFormSyncTimer = null;
	}
	el.classList.remove("is-sync-fresh");
}

/**
 * Copy server values into fields the user has not edited, and mark the row
 * when any of those fields changed.
 *
 * @param {HTMLElement} currentRow - Row already in the modal.
 * @param {HTMLElement} incomingRow - Same item from the refetched form.
 * @returns {void}
 */
function mergeCleanFieldsFromIncoming(currentRow, incomingRow)
{
	const incomingByKey = new Map();
	incomingRow.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!el.name) {
			return;
		}
		incomingByKey.set(orderFormFieldKey(el.name), el);
	});

	let changed = false;
	currentRow.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!isTrackableOrderFormField(el) || isOrderFormControlDirty(el)) {
			return;
		}
		const incoming = incomingByKey.get(orderFormFieldKey(el.name));
		if (!incoming) {
			return;
		}
		const before = normalizeOrderFormValue(el);
		copyOrderFormControlValue(incoming, el);
		const after = normalizeOrderFormValue(el);
		el.dataset.initialValue = after;
		if (before !== after) {
			changed = true;
		}
	});
	if (changed) {
		currentRow.classList.add("is-sync-fresh");
	}
}

/**
 * Visual copy of a row the other user removed.
 * It stays until this form is saved or closed, and it is not submitted.
 *
 * @param {HTMLElement} row - Item row that the other user removed.
 * @returns {HTMLElement}
 */
function buildRemovedOrderFormGhost(row)
{
	const ghost = row.cloneNode(true);
	ghost.classList.remove("order-form-item-row", "is-dirty", "is-pending-delete", "is-sync-fresh");
	ghost.classList.add("order-form-sync-ghost");
	ghost.setAttribute("data-removed-id", orderFormRowInstanceId(row));
	ghost.querySelectorAll("input, select, textarea, button").forEach(function (el) {
		el.disabled = true;
		el.removeAttribute("name");
		el.removeAttribute("id");
	});
	return ghost;
}

/**
 * Count saved item rows and write INITIAL_FORMS. Saved rows stay first.
 *
 * @param {HTMLElement} formsetRoot - Wrapper with data-formset-prefix.
 * @returns {void}
 */
function syncOrderFormsetInitialCount(formsetRoot)
{
	const prefix = formsetRoot.getAttribute("data-formset-prefix");
	const form = formsetRoot.closest("form");
	const tbody = formsetRoot.querySelector("[data-formset-body]");
	const initialInput = form && prefix
		? form.querySelector('[name="' + prefix + '-INITIAL_FORMS"]')
		: null;
	if (!tbody || !initialInput) {
		return;
	}
	let count = 0;
	tbody.querySelectorAll("tr.order-form-item-row").forEach(function (row) {
		if (orderFormRowInstanceId(row)) {
			count += 1;
		}
	});
	initialInput.value = String(count);
}

/**
 * Merge one formset: keep unsaved rows, take server rows the user has not edited,
 * highlight new and changed rows, and fade rows the other user removed.
 *
 * @param {HTMLElement} currentFs - Formset already in the modal.
 * @param {HTMLElement} incomingFs - Same formset from the refetched form.
 * @returns {void}
 */
function mergeOrderFormsetRows(currentFs, incomingFs)
{
	const tbody = currentFs.querySelector("[data-formset-body]");
	if (!tbody) {
		return;
	}
	const addRow = tbody.querySelector(".order-form-add-row");
	const currentRows = Array.from(tbody.querySelectorAll(":scope > tr.order-form-item-row"));
	const incomingRows = Array.from(incomingFs.querySelectorAll("tbody[data-formset-body] > tr.order-form-item-row"));
	const currentById = new Map();
	currentRows.forEach(function (row) {
		const id = orderFormRowInstanceId(row);
		if (id) {
			currentById.set(id, row);
		}
	});

	const incomingIds = new Set();
	const initialRows = [];
	const extraRows = [];
	const ghosts = [];

	incomingRows.forEach(function (incomingRow) {
		const id = orderFormRowInstanceId(incomingRow);
		if (!id) {
			return;
		}
		incomingIds.add(id);
		const currentRow = currentById.get(id);
		if (!currentRow) {
			const fresh = incomingRow.cloneNode(true);
			fresh.classList.add("is-sync-fresh");
			fresh.setAttribute("data-sync-snapshot", "1");
			initialRows.push(fresh);
			return;
		}
		if (orderFormRowHasUnsavedChanges(currentRow)) {
			mergeCleanFieldsFromIncoming(currentRow, incomingRow);
			initialRows.push(currentRow);
			return;
		}
		const changed = orderFormRowSignature(currentRow) !== orderFormRowSignature(incomingRow);
		const replacement = incomingRow.cloneNode(true);
		replacement.setAttribute("data-sync-snapshot", "1");
		if (changed) {
			replacement.classList.add("is-sync-fresh");
		}
		initialRows.push(replacement);
	});

	currentRows.forEach(function (row) {
		const id = orderFormRowInstanceId(row);
		if (id) {
			if (!incomingIds.has(id) && orderFormRowHasUnsavedChanges(row)) {
				initialRows.push(row);
			} else if (!incomingIds.has(id)) {
				ghosts.push(buildRemovedOrderFormGhost(row));
			}
			return;
		}
		if (!isBlankExtraOrderFormRow(row)) {
			extraRows.push(row);
		}
	});

	incomingRows.forEach(function (incomingRow) {
		if (orderFormRowInstanceId(incomingRow)) {
			return;
		}
		const blank = incomingRow.cloneNode(true);
		blank.setAttribute("data-sync-snapshot", "1");
		extraRows.push(blank);
	});

	const nextRows = initialRows.concat(extraRows);

	currentRows.forEach(function (row) {
		row.remove();
	});
	tbody.querySelectorAll(":scope > tr.order-form-sync-ghost").forEach(function (ghost) {
		const removedId = ghost.getAttribute("data-removed-id") || "";
		if (removedId && incomingIds.has(removedId)) {
			ghost.remove();
		}
	});

	nextRows.forEach(function (row) {
		if (addRow) {
			tbody.insertBefore(row, addRow);
		} else {
			tbody.appendChild(row);
		}
	});
	ghosts.forEach(function (ghost) {
		if (addRow) {
			tbody.insertBefore(ghost, addRow);
		} else {
			tbody.appendChild(ghost);
		}
	});

	tbody.querySelectorAll("tr.order-form-item-row[data-sync-snapshot]").forEach(function (row) {
		snapshotOrderFormInitials(row);
		row.removeAttribute("data-sync-snapshot");
	});
	reindexOrderFormsetRows(currentFs);
	syncOrderFormsetInitialCount(currentFs);

	const currentDisplay = Array.from(currentFs.querySelectorAll("thead tr, tr.order-form-totals-row"));
	const incomingDisplay = Array.from(incomingFs.querySelectorAll("thead tr, tr.order-form-totals-row"));
	currentDisplay.forEach(function (row, index) {
		const incomingRow = incomingDisplay[index];
		if (!incomingRow || row.querySelector("input, select, textarea")) {
			return;
		}
		row.innerHTML = incomingRow.innerHTML;
	});
}

/**
 * Update header fields the user has not edited. Dirty fields stay as typed.
 *
 * @param {HTMLFormElement} currentForm - Open modal form.
 * @param {HTMLFormElement} incomingForm - Refetched form.
 * @returns {void}
 */
function mergeOrderFormHeaderFields(currentForm, incomingForm)
{
	const incomingByKey = new Map();
	incomingForm.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!el.name || el.closest("tr.order-form-item-row")) {
			return;
		}
		incomingByKey.set(orderFormControlMatchKey(el), el);
	});

	currentForm.querySelectorAll("input, select, textarea").forEach(function (el) {
		if (!el.name || el.closest("tr.order-form-item-row") || !isTrackableOrderFormField(el)) {
			return;
		}
		const incoming = incomingByKey.get(orderFormControlMatchKey(el));
		if (!incoming || isOrderFormControlDirty(el)) {
			return;
		}
		const before = normalizeOrderFormValue(el);
		copyOrderFormControlValue(incoming, el);
		const after = normalizeOrderFormValue(el);
		el.dataset.initialValue = after;
		if (before !== after) {
			el.classList.add("is-sync-fresh");
		}
	});
}

/**
 * Replace display-only blocks (vitrine info, seal prices) from the refetched form.
 *
 * @param {HTMLFormElement} currentForm - Open modal form.
 * @param {HTMLFormElement} incomingForm - Refetched form.
 * @returns {void}
 */
function mergeOrderFormDisplayBlocks(currentForm, incomingForm)
{
	const currentHeadings = currentForm.querySelectorAll("h4");
	const incomingHeadings = incomingForm.querySelectorAll("h4");
	currentHeadings.forEach(function (heading, index) {
		if (heading.textContent.trim() !== "Информация за поръчка") {
			return;
		}
		const incomingHeading = incomingHeadings[index];
		const currentTable = heading.parentElement && heading.parentElement.querySelector("table");
		const incomingTable = incomingHeading
			&& incomingHeading.parentElement
			&& incomingHeading.parentElement.querySelector("table");
		if (currentTable && incomingTable) {
			currentTable.innerHTML = incomingTable.innerHTML;
		}
	});

	const currentSeal = currentForm.querySelector("#manual-seal-table-wrapper");
	const incomingSeal = incomingForm.querySelector("#manual-seal-table-wrapper");
	if (!currentSeal || !incomingSeal) {
		return;
	}
	const currentReadonly = currentSeal.querySelectorAll("input[readonly]");
	const incomingReadonly = incomingSeal.querySelectorAll("input[readonly]");
	if (currentReadonly.length !== incomingReadonly.length) {
		return;
	}
	currentReadonly.forEach(function (el, index) {
		if (el.name || incomingReadonly[index].name) {
			return;
		}
		el.value = incomingReadonly[index].value;
	});
}

/**
 * Keep the manual-seal radios and panel in step with the checkbox.
 * Does not bind listeners again.
 *
 * @param {ParentNode} form - Modal order form.
 * @returns {void}
 */
function syncManualSealVisual(form)
{
	const checkbox = form.querySelector("#id_vitrine_manual_seal");
	const table = form.querySelector("#manual-seal-table-wrapper");
	const autoMode = form.querySelector("#manual-seal-auto-mode");
	const customMode = form.querySelector("#manual-seal-custom-mode");
	if (!checkbox || !table) {
		return;
	}
	table.classList.toggle("is-open", checkbox.checked);
	if (autoMode && customMode) {
		customMode.checked = checkbox.checked;
		autoMode.checked = !checkbox.checked;
	}
}

/**
 * Banner so the open editor can see that someone else changed this order.
 *
 * @param {HTMLFormElement} form - Modal order form.
 * @returns {void}
 */
function showOrderFormRemoteUpdateNotice(form)
{
	let notice = form.querySelector(".order-form-sync-notice");
	if (notice) {
		const text = notice.querySelector(".order-form-sync-notice-text");
		if (text) {
			text.textContent = ORDER_FORM_REMOTE_UPDATE_MESSAGE;
		}
		return;
	}
	notice = document.createElement("div");
	notice.className = "alert alert-success alert-dismissible fade show order-form-sync-notice text-center mb-3";
	notice.setAttribute("role", "status");
	const text = document.createElement("span");
	text.className = "order-form-sync-notice-text";
	text.textContent = ORDER_FORM_REMOTE_UPDATE_MESSAGE;
	const closeBtn = document.createElement("button");
	closeBtn.type = "button";
	closeBtn.className = "btn-close";
	closeBtn.setAttribute("data-bs-dismiss", "alert");
	closeBtn.setAttribute("aria-label", "Close");
	notice.append(text, closeBtn);
	form.insertBefore(notice, form.firstChild);
}

/**
 * Apply a freshly fetched edit form onto the open one.
 * Unsaved controls and rows stay. Everything else comes from the server.
 *
 * @param {HTMLFormElement} currentForm - Open modal form.
 * @param {string} html - Edit form fragment.
 * @returns {void}
 */
function mergeRemoteOrderFormHtml(currentForm, html)
{
	const holder = document.createElement("div");
	holder.innerHTML = html || "";
	const incomingForm = holder.querySelector("#order-form-modal-form");
	if (!incomingForm) {
		throw new Error("Order form fragment missing");
	}
	if (incomingForm.getAttribute("data-order-id") !== currentForm.getAttribute("data-order-id")) {
		return;
	}

	currentForm.querySelectorAll("[data-formset]").forEach(function (currentFs) {
		const prefix = currentFs.getAttribute("data-formset-prefix");
		const incomingFs = prefix
			? incomingForm.querySelector('[data-formset][data-formset-prefix="' + prefix + '"]')
			: null;
		if (incomingFs) {
			mergeOrderFormsetRows(currentFs, incomingFs);
		}
	});
	mergeOrderFormHeaderFields(currentForm, incomingForm);
	const orderType = currentForm.querySelector("[name='order_type']");
	if (!orderType || !isOrderFormControlDirty(orderType)) {
		syncOrderFormModalTitle(incomingForm, document.getElementById("order-form-modal-title"));
	}
	mergeOrderFormDisplayBlocks(currentForm, incomingForm);
	syncManualSealVisual(currentForm);
	updateOrderFormDirtyState(currentForm);
	showOrderFormRemoteUpdateNotice(currentForm);
	currentForm.querySelectorAll("tr.is-sync-fresh, .is-sync-fresh").forEach(function (el) {
		armOrderFormSyncHighlight(el);
	});
}

/**
 * Fade the open form and show the update spinner.
 *
 * @param {boolean} active - Whether a remote merge is in progress.
 * @returns {void}
 */
function setOrderFormSyncing(active)
{
	const body = document.getElementById("order-form-modal-body");
	if (!body) {
		return;
	}
	body.classList.toggle("is-syncing", active);
	let overlay = body.querySelector(".order-form-sync-overlay");
	if (!active) {
		if (overlay) {
			overlay.remove();
		}
		return;
	}
	if (!overlay) {
		overlay = document.createElement("div");
		overlay.className = "order-form-sync-overlay";
		overlay.setAttribute("role", "status");
		overlay.innerHTML = ""
			+ '<div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>'
			+ "<p class=\"mb-0\">" + ORDER_FORM_REMOTE_UPDATE_MESSAGE + "</p>"
			+ "<p class=\"mb-0\">Зареждане на промените...</p>";
		body.insertBefore(overlay, body.firstChild);
	}
}

/**
 * Drop a remote merge that belongs to a modal which has since closed.
 *
 * @returns {void}
 */
function invalidateOrderFormRemoteSync()
{
	orderFormRemoteSyncToken += 1;
	orderFormRemoteSyncQueued = false;
	orderFormRemoteSyncInFlight = false;
	setOrderFormSyncing(false);
}

/**
 * Order id from an edit form URL (`/orderForm/<id>`).
 *
 * @param {string} url - Form URL.
 * @returns {string}
 */
function orderIdFromOrderFormUrl(url)
{
	const match = String(url || "").match(/\/orderForm\/(\d+)/);
	return match ? match[1] : "";
}

/**
 * True when the edit modal is open for this order.
 *
 * @param {string} orderId - Order / vitrine id.
 * @returns {HTMLFormElement|null}
 */
function openEditOrderForm(orderId)
{
	const modal = document.getElementById("order-form-modal");
	const form = document.getElementById("order-form-modal-form");
	if (!modal || !modal.classList.contains("show") || !form) {
		return null;
	}
	if (String(form.getAttribute("data-order-id") || "") !== String(orderId)) {
		return null;
	}
	return form;
}

/**
 * Start a queued remote merge once the form and any save are idle.
 *
 * @returns {void}
 */
function flushQueuedOrderFormRemoteSync()
{
	if (!orderFormRemoteSyncQueued || orderFormSubmitInFlight || orderFormRemoteSyncInFlight) {
		return;
	}
	orderFormRemoteSyncQueued = false;
	runOrderFormRemoteSync();
}

/**
 * Refetch the open edit form and merge it without dropping unsaved edits.
 *
 * @returns {Promise<void>}
 */
async function runOrderFormRemoteSync()
{
	const modal = document.getElementById("order-form-modal");
	const form = document.getElementById("order-form-modal-form");
	const url = modal && modal.dataset.orderFormUrl;
	const orderId = form && form.getAttribute("data-order-id");
	if (!modal || !modal.classList.contains("show") || !form || !orderId || !url) {
		return;
	}

	const token = ++orderFormRemoteSyncToken;
	orderFormRemoteSyncInFlight = true;
	setOrderFormSyncing(true);
	try {
		const response = await fetch(url, {
			method: "GET",
			credentials: "same-origin",
			headers: { "X-Requested-With": "XMLHttpRequest" }
		});
		if (typeof redirectToLoginIfUnauthenticated === "function"
			&& redirectToLoginIfUnauthenticated(response)) {
			return;
		}
		if (response.status === 404) {
			return;
		}
		if (!response.ok) {
			throw new Error("Order form refresh failed");
		}
		const html = await response.text();
		if (token !== orderFormRemoteSyncToken) {
			return;
		}
		const currentForm = openEditOrderForm(orderId);
		if (!currentForm) {
			return;
		}
		mergeRemoteOrderFormHtml(currentForm, html);
	} catch (err) {
		if (token === orderFormRemoteSyncToken) {
			console.error(err);
			showOrderFormToast("Възникна грешка при зареждане на промените.", "error");
		}
	} finally {
		if (token !== orderFormRemoteSyncToken) {
			return;
		}
		setOrderFormSyncing(false);
		orderFormRemoteSyncInFlight = false;
		flushQueuedOrderFormRemoteSync();
	}
}

/**
 * Live sync changed an order. If its edit modal is open, merge that form.
 * A closed modal is left alone; opening it loads the form fresh.
 *
 * @param {Array<string|number>} orderIds - Order ids updated by someone else.
 * @returns {void}
 */
function syncOpenOrderFormFromLiveUpdate(orderIds)
{
	const modal = document.getElementById("order-form-modal");
	if (!modal || !modal.classList.contains("show") || !Array.isArray(orderIds) || !orderIds.length) {
		return;
	}
	const form = document.getElementById("order-form-modal-form");
	const openId = (form && form.getAttribute("data-order-id"))
		|| orderIdFromOrderFormUrl(modal.dataset.orderFormUrl);
	if (!openId || !orderIds.some(function (id) { return String(id) === String(openId); })) {
		return;
	}
	orderFormRemoteSyncQueued = true;
	flushQueuedOrderFormRemoteSync();
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

	const wasCreate = !form.getAttribute("data-order-id");
	orderFormSubmitInFlight = true;
	const submitForm = cloneOrderFormWithValues(form);
	prepareOrderFormsetsForSubmit(submitForm);
	const postedInitials = collectOrderFormInitials(submitForm);

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
			showOrderFormToast(orderFormSuccessMessage(data.id), "success");
			if (wasCreate) {
				if (data.form_html) {
					setOrderFormModalBody(data.form_html);
				}
			} else {
				closeOrderFormModal();
			}
		})
		.catch(function (err) {
			window.clearTimeout(timeoutId);
			console.error(err);
			if (err && err.formHtml) {
				setOrderFormModalBody(err.formHtml, { initials: postedInitials });
			} else if (saveBtn) {
				saveBtn.disabled = false;
				saveBtn.innerHTML = oldHtml;
			}
			showOrderFormToast(
				(err && err.userMessage) || "Възникна грешка!",
				"error"
			);
		})
		.finally(function () {
			orderFormSubmitInFlight = false;
			flushQueuedOrderFormRemoteSync();
		});
}

/**
 * Bind create/edit intercepts, add-row, dirty tracking, and submit.
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
			const currentView = root && root.dataset.currentView;
			if (currentView === "table") {
				event.preventDefault();
				openOrderFormModal(addLink.dataset.tableFormUrl);
				return;
			}
			if (currentView === "vitrine") {
				event.preventDefault();
				openOrderFormModal(addLink.dataset.vitrineFormUrl);
				return;
			}
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
		}
	});

	parts.modal.addEventListener("input", function (event) {
		const form = event.target.closest("#order-form-modal-form");
		if (form) {
			updateOrderFormDirtyState(form);
		}
	});

	parts.modal.addEventListener("change", function (event) {
		const form = event.target.closest("#order-form-modal-form");
		if (form) {
			updateOrderFormDirtyState(form);
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

	parts.modal.addEventListener("show.bs.modal", function () {
		parts.modal.inert = false;
	});

	parts.modal.addEventListener("hide.bs.modal", function (event) {
		if (allowOrderFormClose) {
			allowOrderFormClose = false;
			hideOrderFormUnsavedDialog();
			releaseOrderFormModalFocus(parts.modal);
			return;
		}
		if (!orderFormHasUnsavedChanges()) {
			releaseOrderFormModalFocus(parts.modal);
			return;
		}
		event.preventDefault();
		showOrderFormUnsavedDialog();
	});

	const unsavedDialog = orderFormUnsavedDialog();
	if (unsavedDialog) {
		unsavedDialog.addEventListener("click", function (event) {
			if (event.target.closest("[data-order-form-unsaved-cancel]")) {
				hideOrderFormUnsavedDialog();
				return;
			}
			if (event.target.closest("#order-form-unsaved-confirm")) {
				closeOrderFormModal();
			}
		});
	}

	const clearFreshFromEvent = function (event) {
		const row = event.target.closest("tr.is-sync-fresh");
		if (row) {
			clearOrderFormSyncHighlight(row);
		}
		const field = event.target.closest(".is-sync-fresh");
		if (field && field !== row) {
			clearOrderFormSyncHighlight(field);
		}
	};
	parts.modal.addEventListener("focusin", clearFreshFromEvent);
	parts.modal.addEventListener("pointerdown", clearFreshFromEvent);

	parts.modal.addEventListener("hidden.bs.modal", function () {
		hideOrderFormUnsavedDialog();
		invalidateOrderFormRemoteSync();
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
