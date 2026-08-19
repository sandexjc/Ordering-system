/*
 * dynamic/filters.js
 * ------------------
 * Filter / sort / range-slider state and UI for the dynamic orders page.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - dynamic/state.js
 *   - dynamic/session.js → redirectToLoginIfUnauthenticated
 * Runtime depends on:
 *   - dynamic/fetch.js  → beginOrdersRender, fetchAndRenderOrders, getLiveOrdersBody
 *   - dynamic/search.js → getSearchForView, isSearchActive
 */

/** Update top counter text to match currently rendered rows.
 * @param {*} visibleItems - Number of currently visible list items.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function updateVisibleItemsCounter(visibleItems, viewName = null) {
    const itemsNode = document.getElementById("visible-items-count");
    const suffixNode = document.getElementById("visible-items-suffix");

    if (itemsNode) {
        itemsNode.textContent = visibleItems;
    }
    if (suffixNode) {
        suffixNode.textContent = visibleItems === 1 ? "" : "a";
    }

    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    updateVisibleFiltersSummary(getFiltersForView(resolvedView), resolvedView);
}

/**
 * getDefaultOrderFilters
 * @returns {Object}
 */
function getDefaultOrderFilters() {
    return {
        sortBy: DEFAULT_ORDER_FILTERS.sortBy,
        sortDir: DEFAULT_ORDER_FILTERS.sortDir,
        start: DEFAULT_ORDER_FILTERS.start,
        end: DEFAULT_ORDER_FILTERS.end,
        includeOrder: DEFAULT_ORDER_FILTERS.includeOrder,
        includeOffer: DEFAULT_ORDER_FILTERS.includeOffer,
        idMin: DEFAULT_ORDER_FILTERS.idMin,
        idMax: DEFAULT_ORDER_FILTERS.idMax,
        balanceMin: DEFAULT_ORDER_FILTERS.balanceMin,
        balanceMax: DEFAULT_ORDER_FILTERS.balanceMax,
    };
}

/** Parse a finite number or return null.
 * @param {*} value - Input value to parse or escape.
 * @returns {number|null}
 */
function parseOptionalNumber(value) {
    if (value === null || value === undefined || value === "") {
        return null;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
}

/** Normalize legacy/partial filter objects into the current shape.
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @returns {Object}
 */
function normalizeOrderFilters(filters) {
    const normalized = getDefaultOrderFilters();
    if (!filters || typeof filters !== "object") {
        return normalized;
    }

    if (filters.sortBy === "order_id" || filters.sortBy === "date" || filters.sortBy === "balance") {
        normalized.sortBy = filters.sortBy;
    }
    if (filters.sortDir === "asc" || filters.sortDir === "desc") {
        normalized.sortDir = filters.sortDir;
    } else if (filters.sort === "asc" || filters.sort === "desc") {
        // Backward compatible with the previous sort-only filter shape.
        normalized.sortDir = filters.sort;
    }

    normalized.start = filters.start || null;
    normalized.end = filters.end || null;
    normalized.includeOrder = Boolean(filters.includeOrder);
    normalized.includeOffer = Boolean(filters.includeOffer);
    normalized.idMin = parseOptionalNumber(filters.idMin);
    normalized.idMax = parseOptionalNumber(filters.idMax);
    normalized.balanceMin = parseOptionalNumber(filters.balanceMin);
    normalized.balanceMax = parseOptionalNumber(filters.balanceMax);
    return normalized;
}

/** Active filters for a view (falls back to defaults).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {Object}
 */
function getFiltersForView(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    if (cacheEntry && cacheEntry.filters) {
        return normalizeOrderFilters(cacheEntry.filters);
    }
    return getDefaultOrderFilters();
}

/** True when id/balance values differ from the full available bounds (or bounds unknown).
 * @param {*} minValue - Range minimum value.
 * @param {*} maxValue - Range maximum value.
 * @param {*} boundMin - Available minimum bound.
 * @param {*} boundMax - Available maximum bound.
 * @returns {boolean}
 */
function isRangeFilterActive(minValue, maxValue, boundMin, boundMax) {
    if (minValue == null && maxValue == null) {
        return false;
    }
    if (boundMin == null || boundMax == null) {
        return minValue != null || maxValue != null;
    }
    const effectiveMin = minValue == null ? boundMin : minValue;
    const effectiveMax = maxValue == null ? boundMax : maxValue;
    return effectiveMin > boundMin || effectiveMax < boundMax;
}

/** True when filters differ from defaults (drives the toolbar badge). Sort is table-driven and ignored here.
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {boolean}
 */
function filtersAreActive(filters, viewName = null) {
    const current = normalizeOrderFilters(filters);
    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    const bounds = getFilterBoundsForView(resolvedView);

    return (
        Boolean(current.start)
        || Boolean(current.end)
        || current.includeOrder !== DEFAULT_ORDER_FILTERS.includeOrder
        || current.includeOffer !== DEFAULT_ORDER_FILTERS.includeOffer
        || isRangeFilterActive(current.idMin, current.idMax, bounds?.idMin, bounds?.idMax)
        || isRangeFilterActive(
            current.balanceMin,
            current.balanceMax,
            bounds?.balanceMin,
            bounds?.balanceMax
        )
    );
}

/** Toggle the red filter badge and enable/disable the reset button.
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function updateFilterBadge(filters, viewName = null) {
    const active = filtersAreActive(filters, viewName);
    const badge = document.getElementById("dynamic-filter-badge");
    if (badge) {
        badge.classList.toggle("d-none", !active);
    }

    const resetButton = document.getElementById("dynamic-filter-reset");
    if (resetButton) {
        resetButton.disabled = !active;
    }
}

/** Format YYYY-MM-DD for display under date buttons.
 * @param {*} value - Input value to parse or escape.
 * @returns {string}
 */
function formatFilterDateLabel(value) {
    if (!value) {
        return "—";
    }
    const parts = value.split("-");
    if (parts.length !== 3) {
        return value;
    }
    return `${parts[2]}.${parts[1]}.${parts[0]}`;
}

/** Stored min/max bounds for id/balance sliders per view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {*}
 */
function getFilterBoundsForView(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    return cacheEntry?.filterBounds || null;
}

/** Resolve endpoint URL for the given dynamic view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {*}
 */
function getOrdersEndpointForView(viewName) {
    const liveBody = typeof getLiveOrdersBody === "function" ? getLiveOrdersBody(viewName) : null;
    if (liveBody?.dataset.endpoint) {
        return liveBody.dataset.endpoint;
    }
    const template = document.getElementById(`dynamic-${viewName}-shell-template`);
    if (template) {
        const probe = document.createElement("div");
        probe.innerHTML = template.innerHTML;
        const body = probe.querySelector("#dynamic-orders-body");
        if (body?.dataset.endpoint) {
            return body.dataset.endpoint;
        }
    }
    return document.getElementById("dynamic-orders-body")?.dataset.endpoint || null;
}

/** Fetch and cache id/balance slider bounds for a view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {Promise<void>}
 */
async function ensureFilterBounds(viewName) {
    const existing = getFilterBoundsForView(viewName);
    if (existing) {
        return existing;
    }

    const endpoint = getOrdersEndpointForView(viewName);
    if (!endpoint) {
        return null;
    }

    try {
        const url = new URL(endpoint, window.location.origin);
        url.searchParams.set("bounds", "1");
        const response = await fetch(url.toString(), {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (typeof redirectToLoginIfUnauthenticated === "function"
            && redirectToLoginIfUnauthenticated(response)) {
            return null;
        }
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const payload = await response.json();
        const bounds = {
            idMin: Number(payload.id_min) || 0,
            idMax: Number(payload.id_max) || 0,
            balanceMin: Number(payload.balance_min) || 0,
            balanceMax: Number(payload.balance_max) || 0,
        };
        if (bounds.idMax < bounds.idMin) {
            bounds.idMax = bounds.idMin;
        }
        if (bounds.balanceMax < bounds.balanceMin) {
            bounds.balanceMax = bounds.balanceMin;
        }
        updateViewCache(viewName, { filterBounds: bounds });
        return bounds;
    } catch (error) {
        console.error(error);
        return null;
    }
}

/** Map range key to filter state field names.
 * @param {*} rangeKey - Range filter key (order_id | balance).
 * @returns {Object}
 */
function getRangeFilterFields(rangeKey) {
    if (rangeKey === "order_id") {
        return { minKey: "idMin", maxKey: "idMax", boundMinKey: "idMin", boundMaxKey: "idMax" };
    }
    return {
        minKey: "balanceMin",
        maxKey: "balanceMax",
        boundMinKey: "balanceMin",
        boundMaxKey: "balanceMax",
    };
}

/** Read the DOM controls for a range filter panel.
 * @param {*} rangeKey - Range filter key (order_id | balance).
 * @returns {*}
 */
function getRangeFilterElements(rangeKey) {
    const root = document.querySelector(`.dynamic-range-filter[data-range-key="${rangeKey}"]`);
    if (!root) {
        return null;
    }
    return {
        root,
        minRange: root.querySelector(".dynamic-range-min"),
        maxRange: root.querySelector(".dynamic-range-max"),
        minInput: root.querySelector(".dynamic-range-min-input"),
        maxInput: root.querySelector(".dynamic-range-max-input"),
    };
}

/** Convert current slider/input values into filter patch (null/null = all).
 * @param {*} rangeKey - Range filter key (order_id | balance).
 * @param {*} minValue - Range minimum value.
 * @param {*} maxValue - Range maximum value.
 * @param {*} bounds - Filter bounds object for id/balance.
 * @returns {string}
 */
function buildRangeFilterPatch(rangeKey, minValue, maxValue, bounds) {
    const fields = getRangeFilterFields(rangeKey);
    const boundMin = bounds?.[fields.boundMinKey];
    const boundMax = bounds?.[fields.boundMaxKey];
    let nextMin = parseOptionalNumber(minValue);
    let nextMax = parseOptionalNumber(maxValue);

    if (nextMin != null && nextMax != null && nextMin > nextMax) {
        const swap = nextMin;
        nextMin = nextMax;
        nextMax = swap;
    }

    if (
        boundMin != null
        && boundMax != null
        && (nextMin == null || nextMin <= boundMin)
        && (nextMax == null || nextMax >= boundMax)
    ) {
        return { [fields.minKey]: null, [fields.maxKey]: null };
    }

    return { [fields.minKey]: nextMin, [fields.maxKey]: nextMax };
}

/** Push filter values into a range slider + number fields.
 * @param {*} rangeKey - Range filter key (order_id | balance).
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @param {*} bounds - Filter bounds object for id/balance.
 * @returns {void}
 */
function syncRangeFilterControls(rangeKey, filters, bounds) {
    const elements = getRangeFilterElements(rangeKey);
    if (!elements) {
        return;
    }

    const fields = getRangeFilterFields(rangeKey);
    const boundMin = bounds?.[fields.boundMinKey] ?? 0;
    const boundMax = bounds?.[fields.boundMaxKey] ?? 0;
    const valueMin = filters[fields.minKey] == null ? boundMin : filters[fields.minKey];
    const valueMax = filters[fields.maxKey] == null ? boundMax : filters[fields.maxKey];

    [elements.minRange, elements.maxRange].forEach((rangeInput) => {
        if (!rangeInput) {
            return;
        }
        rangeInput.min = String(boundMin);
        rangeInput.max = String(boundMax);
        rangeInput.step = rangeKey === "balance" ? "0.01" : "1";
    });

    if (elements.minRange) {
        elements.minRange.value = String(valueMin);
    }
    if (elements.maxRange) {
        elements.maxRange.value = String(valueMax);
    }
    if (elements.minInput) {
        elements.minInput.min = String(boundMin);
        elements.minInput.max = String(boundMax);
        elements.minInput.value = String(valueMin);
    }
    if (elements.maxInput) {
        elements.maxInput.min = String(boundMin);
        elements.maxInput.max = String(boundMax);
        elements.maxInput.value = String(valueMax);
    }
}

/** Debounced apply for range slider/input changes.
 * @param {*} rangeKey - Range filter key (order_id | balance).
 * @returns {void}
 */
function scheduleRangeFilterCommit(rangeKey) {
    const elements = getRangeFilterElements(rangeKey);
    if (!elements) {
        return;
    }

    const root = document.getElementById("dynamic-orders-root");
    const viewName = root?.dataset.currentView || "table";
    const bounds = getFilterBoundsForView(viewName);

    if (rangeFilterDebounceTimer) {
        window.clearTimeout(rangeFilterDebounceTimer);
    }
    rangeFilterDebounceTimer = window.setTimeout(() => {
        rangeFilterDebounceTimer = null;
        const patch = buildRangeFilterPatch(
            rangeKey,
            elements.minInput?.value,
            elements.maxInput?.value,
            bounds
        );
        applyFiltersAndRefresh(patch);
    }, RANGE_FILTER_DEBOUNCE_MS);
}

/** Wire one dual-range control set.
 * @param {*} rangeKey - Range filter key (order_id | balance).
 * @returns {void}
 */
function bindRangeFilterControls(rangeKey) {
    const elements = getRangeFilterElements(rangeKey);
    if (!elements || elements.root.dataset.rangeBound === "1") {
        return;
    }
    elements.root.dataset.rangeBound = "1";

    const syncFromRanges = () => {
        let minValue = parseOptionalNumber(elements.minRange.value);
        let maxValue = parseOptionalNumber(elements.maxRange.value);
        if (minValue != null && maxValue != null && minValue > maxValue) {
            if (document.activeElement === elements.minRange) {
                maxValue = minValue;
                elements.maxRange.value = String(maxValue);
            } else {
                minValue = maxValue;
                elements.minRange.value = String(minValue);
            }
        }
        elements.minInput.value = String(minValue ?? "");
        elements.maxInput.value = String(maxValue ?? "");
        scheduleRangeFilterCommit(rangeKey);
    };

    const syncFromInputs = () => {
        let minValue = parseOptionalNumber(elements.minInput.value);
        let maxValue = parseOptionalNumber(elements.maxInput.value);
        if (minValue != null && maxValue != null && minValue > maxValue) {
            const swap = minValue;
            minValue = maxValue;
            maxValue = swap;
            elements.minInput.value = String(minValue);
            elements.maxInput.value = String(maxValue);
        }
        if (minValue != null) {
            elements.minRange.value = String(minValue);
        }
        if (maxValue != null) {
            elements.maxRange.value = String(maxValue);
        }
        scheduleRangeFilterCommit(rangeKey);
    };

    elements.minRange.addEventListener("input", syncFromRanges);
    elements.maxRange.addEventListener("input", syncFromRanges);
    elements.minInput.addEventListener("change", syncFromInputs);
    elements.maxInput.addEventListener("change", syncFromInputs);
}

/** Build the compact “what filters are applied” text.
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {string}
 */
function buildVisibleFiltersSummary(filters, viewName = null) {
    const current = normalizeOrderFilters(filters);
    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    const bounds = getFilterBoundsForView(resolvedView);
    const parts = [];

    const types = [];
    if (current.includeOrder) {
        types.push("поръчки");
    }
    if (current.includeOffer) {
        types.push("оферти");
    }
    parts.push(types.length ? `вид: ${types.join(" + ")}` : "вид: няма");

    if (current.start || current.end) {
        const startLabel = current.start ? formatFilterDateLabel(current.start) : "…";
        const endLabel = current.end ? formatFilterDateLabel(current.end) : "…";
        parts.push(`период: ${startLabel} – ${endLabel}`);
    }

    if (isRangeFilterActive(current.idMin, current.idMax, bounds?.idMin, bounds?.idMax)) {
        const minLabel = current.idMin == null ? bounds?.idMin ?? "…" : current.idMin;
        const maxLabel = current.idMax == null ? bounds?.idMax ?? "…" : current.idMax;
        parts.push(`номер: ${minLabel} – ${maxLabel}`);
    }

    if (
        isRangeFilterActive(
            current.balanceMin,
            current.balanceMax,
            bounds?.balanceMin,
            bounds?.balanceMax
        )
    ) {
        const minLabel =
            current.balanceMin == null ? bounds?.balanceMin ?? "…" : current.balanceMin;
        const maxLabel =
            current.balanceMax == null ? bounds?.balanceMax ?? "…" : current.balanceMax;
        parts.push(`баланс: ${minLabel} – ${maxLabel}`);
    }

    return parts.join(" · ");
}

/** Update the filter/search summary below the counter (only when non-default).
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function updateVisibleFiltersSummary(filters, viewName = null) {
    const summaryNode = document.getElementById("visible-items-filters");
    if (!summaryNode) {
        return;
    }

    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    const current = normalizeOrderFilters(filters);
    const searchQuery = getSearchForView(resolvedView);
    const parts = [];

    if (filtersAreActive(current, resolvedView)) {
        parts.push(buildVisibleFiltersSummary(current, resolvedView));
    }
    if (isSearchActive(searchQuery)) {
        parts.push(`търсене: ${searchQuery.trim()}`);
    }

    if (!parts.length) {
        summaryNode.textContent = "";
        summaryNode.classList.add("d-none");
        return;
    }

    summaryNode.textContent = parts.join(" · ");
    summaryNode.classList.remove("d-none");
}

/** Sync red sort arrows on the live table headers.
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @returns {void}
 */
function syncSortHeaders(filters) {
    const current = normalizeOrderFilters(filters);
    const container = document.getElementById("dynamic-orders-table-container");
    if (!container) {
        return;
    }

    container.querySelectorAll("th[data-sort-by]").forEach((th) => {
        const sortBy = th.dataset.sortBy;
        const arrow = th.querySelector(".sort-arrow");
        const isActive = sortBy === current.sortBy;
        th.classList.toggle("is-sorted", isActive);
        th.setAttribute(
            "aria-sort",
            isActive ? (current.sortDir === "asc" ? "ascending" : "descending") : "none"
        );
        if (arrow) {
            arrow.textContent = isActive ? (current.sortDir === "asc" ? "▲" : "▼") : "";
        }
    });
}

/** Sync filter controls to the given filter state (no refetch).
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function syncFilterControls(filters, viewName = null) {
    const current = normalizeOrderFilters(filters);
    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    const bounds = getFilterBoundsForView(resolvedView);

    const orderCheckbox = document.getElementById("filter-type-order");
    const offerCheckbox = document.getElementById("filter-type-offer");
    if (orderCheckbox) {
        orderCheckbox.checked = Boolean(current.includeOrder);
    }
    if (offerCheckbox) {
        offerCheckbox.checked = Boolean(current.includeOffer);
    }

    const startDisplay = document.getElementById("filter-start-display");
    const endDisplay = document.getElementById("filter-end-display");
    if (startDisplay) {
        startDisplay.textContent = formatFilterDateLabel(current.start);
    }
    if (endDisplay) {
        endDisplay.textContent = formatFilterDateLabel(current.end);
    }

    const dateInput = document.getElementById("dynamic-filter-date-input");
    const dateTarget = document.querySelector('input[name="filter-date-target"]:checked');
    if (dateInput && dateTarget) {
        dateInput.value = current[dateTarget.value] || "";
    }

    syncRangeFilterControls("order_id", current, bounds);
    syncRangeFilterControls("balance", current, bounds);
    syncSortHeaders(current);
    updateFilterBadge(current, resolvedView);
    updateVisibleFiltersSummary(current, resolvedView);
}

/** Show the options panel for the selected filter category.
 * @param {*} category - Filter category panel id (type/date/...).
 * @returns {void}
 */
function showFilterCategoryPanel(category) {
    document.querySelectorAll("[data-filter-panel]").forEach((panel) => {
        panel.classList.toggle("d-none", panel.dataset.filterPanel !== category);
    });

    const calendarPanel = document.getElementById("dynamic-filter-calendar-panel");

    if (category === "date") {
        const dateTarget = document.querySelector('input[name="filter-date-target"]:checked');
        if (calendarPanel) {
            calendarPanel.classList.toggle("d-none", !dateTarget);
        }
        return;
    }

    if (calendarPanel) {
        calendarPanel.classList.add("d-none");
    }
    const dateTarget = document.querySelector('input[name="filter-date-target"]:checked');
    if (dateTarget) {
        dateTarget.checked = false;
    }
}

/** Open the calendar column for start/end date editing.
 * @param {*} target - Date filter target ("start" | "end").
 * @param {*} filters - Order filter object (sort, dates, types, ranges).
 * @returns {void}
 */
function openDateCalendar(target, filters) {
    const calendarPanel = document.getElementById("dynamic-filter-calendar-panel");
    const calendarLabel = document.getElementById("dynamic-filter-calendar-label");
    const dateInput = document.getElementById("dynamic-filter-date-input");
    if (!calendarPanel || !dateInput) {
        return;
    }

    calendarPanel.classList.remove("d-none");
    if (calendarLabel) {
        calendarLabel.textContent = target === "start" ? "Начална дата" : "Крайна дата";
    }
    dateInput.dataset.dateTarget = target;
    dateInput.value = filters[target] || "";

    window.requestAnimationFrame(() => {
        dateInput.focus();
        if (typeof dateInput.showPicker === "function") {
            try {
                dateInput.showPicker();
            } catch (error) {
                // Browser may block showPicker without a direct gesture; input remains usable.
            }
        }
    });
}

/** Persist filters, clear cached rows, and refetch the active view.
 * @param {*} patch - Partial filter or cache fields to merge.
 * @returns {void}
 */
function applyFiltersAndRefresh(patch) {
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }

    const viewName = root.dataset.currentView || "table";
    const filters = normalizeOrderFilters({ ...getFiltersForView(viewName), ...patch });

    updateViewCache(viewName, {
        filters,
        rowsHtml: "",
        visibleItems: 0,
        nextCursor: null,
        hasMore: false,
        openRowIds: [],
        orderDetails: {},
        scrollY: 0,
    });
    syncFilterControls(filters, viewName);
    updateVisibleItemsCounter(0, viewName);

    const { generation } = beginOrdersRender(viewName);
    fetchAndRenderOrders({ forceRefresh: true, viewName, generation });
}

/**
 * Reset period/type/range filters for the active view; keep current table sort.
 * @returns {void}
 */
function resetFiltersAndRefresh() {
    const root = document.getElementById("dynamic-orders-root");
    const viewName = root?.dataset.currentView || "table";
    const current = getFiltersForView(viewName);
    applyFiltersAndRefresh({
        ...getDefaultOrderFilters(),
        sortBy: current.sortBy,
        sortDir: current.sortDir,
    });
}

/** Handle click/keyboard on a sortable table header.
 * @param {*} sortBy - Sort field (order_id | date | balance).
 * @returns {void}
 */
function handleSortHeaderClick(sortBy) {
    if (sortBy !== "order_id" && sortBy !== "date" && sortBy !== "balance") {
        return;
    }

    const root = document.getElementById("dynamic-orders-root");
    const viewName = root?.dataset.currentView || "table";
    const current = getFiltersForView(viewName);
    const sortDir =
        current.sortBy === sortBy && current.sortDir === "desc" ? "asc" : "desc";

    applyFiltersAndRefresh({ sortBy, sortDir });
}

/**
 * Wire delegated click/keyboard handlers for sortable headers.
 * @returns {void}
 */
function setupTableSortHeaders() {
    const container = document.getElementById("dynamic-orders-table-container");
    if (!container || container.dataset.sortBound === "1") {
        return;
    }
    container.dataset.sortBound = "1";

    container.addEventListener("click", (event) => {
        const th = event.target.closest("th[data-sort-by]");
        if (!th || !container.contains(th)) {
            return;
        }
        event.preventDefault();
        handleSortHeaderClick(th.dataset.sortBy);
    });

    container.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }
        const th = event.target.closest("th[data-sort-by]");
        if (!th || !container.contains(th)) {
            return;
        }
        event.preventDefault();
        handleSortHeaderClick(th.dataset.sortBy);
    });
}

/**
 * Wire filter UI events (category panels + immediate filter applies).
 * @returns {void}
 */
function setupDynamicFilters() {
    const filterRoot = document.getElementById("collapseExample");
    if (!filterRoot || filterRoot.dataset.filtersBound === "1") {
        return;
    }
    filterRoot.dataset.filtersBound = "1";

    const root = document.getElementById("dynamic-orders-root");
    const initialView = root?.dataset.currentView || "table";
    bindRangeFilterControls("order_id");
    bindRangeFilterControls("balance");
    syncFilterControls(getFiltersForView(initialView), initialView);
    showFilterCategoryPanel("type");
    ensureFilterBounds(initialView).then((bounds) => {
        if (!bounds) {
            return;
        }
        syncFilterControls(getFiltersForView(initialView), initialView);
    });

    filterRoot.querySelectorAll('input[name="filter-category"]').forEach((input) => {
        input.addEventListener("change", () => {
            if (input.checked) {
                showFilterCategoryPanel(input.value);
            }
        });
    });

    filterRoot.querySelectorAll('input[name="filter-date-target"]').forEach((input) => {
        input.addEventListener("change", () => {
            if (!input.checked) {
                return;
            }
            const viewName = root?.dataset.currentView || "table";
            openDateCalendar(input.value, getFiltersForView(viewName));
        });
    });

    const dateInput = document.getElementById("dynamic-filter-date-input");
    if (dateInput) {
        dateInput.addEventListener("change", () => {
            const target = dateInput.dataset.dateTarget;
            if (target !== "start" && target !== "end") {
                return;
            }
            applyFiltersAndRefresh({ [target]: dateInput.value || null });
        });
    }

    const orderCheckbox = document.getElementById("filter-type-order");
    const offerCheckbox = document.getElementById("filter-type-offer");
    const onTypeChange = () => {
        applyFiltersAndRefresh({
            includeOrder: Boolean(orderCheckbox?.checked),
            includeOffer: Boolean(offerCheckbox?.checked),
        });
    };
    if (orderCheckbox) {
        orderCheckbox.addEventListener("change", onTypeChange);
    }
    if (offerCheckbox) {
        offerCheckbox.addEventListener("change", onTypeChange);
    }

    const resetButton = document.getElementById("dynamic-filter-reset");
    if (resetButton) {
        resetButton.addEventListener("click", () => {
            resetFiltersAndRefresh();
            const typeCategory = document.getElementById("filter-cat-type");
            if (typeCategory) {
                typeCategory.checked = true;
                showFilterCategoryPanel("type");
            }
        });
    }
}
