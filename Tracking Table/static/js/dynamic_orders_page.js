/** Update top counter text to match currently rendered rows. */
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
    updateVisibleFiltersSummary(getFiltersForView(resolvedView));
}

/** Cache rows per view to avoid re-fetching on tab switch. */
const viewOrdersCache = window.viewOrdersCache || new Map();
window.viewOrdersCache = viewOrdersCache;

let infiniteScrollObserver = null;
let isLoadingMore = false;
/** Bumped on every view switch / top-level render so stale async work cannot touch the wrong tab. */
let ordersRenderGeneration = 0;

/** Default list filters (newest by date, orders only). */
const DEFAULT_ORDER_FILTERS = Object.freeze({
    sortBy: "date",
    sortDir: "desc",
    start: null,
    end: null,
    includeOrder: true,
    includeOffer: false,
});

const SORT_BY_LABELS = {
    order_id: "номер",
    date: "дата",
    balance: "баланс",
};

/** Clone default filters. */
function getDefaultOrderFilters() {
    return {
        sortBy: DEFAULT_ORDER_FILTERS.sortBy,
        sortDir: DEFAULT_ORDER_FILTERS.sortDir,
        start: DEFAULT_ORDER_FILTERS.start,
        end: DEFAULT_ORDER_FILTERS.end,
        includeOrder: DEFAULT_ORDER_FILTERS.includeOrder,
        includeOffer: DEFAULT_ORDER_FILTERS.includeOffer,
    };
}

/** Normalize legacy/partial filter objects into the current shape. */
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
    return normalized;
}

/** Active filters for a view (falls back to defaults). */
function getFiltersForView(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    if (cacheEntry && cacheEntry.filters) {
        return normalizeOrderFilters(cacheEntry.filters);
    }
    return getDefaultOrderFilters();
}

/** True when filters differ from defaults (drives the toolbar badge). */
function filtersAreActive(filters) {
    const current = normalizeOrderFilters(filters);
    return (
        current.sortBy !== DEFAULT_ORDER_FILTERS.sortBy
        || current.sortDir !== DEFAULT_ORDER_FILTERS.sortDir
        || Boolean(current.start)
        || Boolean(current.end)
        || current.includeOrder !== DEFAULT_ORDER_FILTERS.includeOrder
        || current.includeOffer !== DEFAULT_ORDER_FILTERS.includeOffer
    );
}

/** Toggle the red filter badge and enable/disable the reset button. */
function updateFilterBadge(filters) {
    const active = filtersAreActive(filters);
    const badge = document.getElementById("dynamic-filter-badge");
    if (badge) {
        badge.classList.toggle("d-none", !active);
    }

    const resetButton = document.getElementById("dynamic-filter-reset");
    if (resetButton) {
        resetButton.disabled = !active;
    }
}

/** Format YYYY-MM-DD for display under date buttons. */
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

/** Human-readable direction label for the active sort field. */
function formatSortDirectionLabel(sortBy, sortDir) {
    if (sortBy === "date") {
        return sortDir === "asc" ? "най-стари" : "най-нови";
    }
    return sortDir === "asc" ? "възходящо" : "низходящо";
}

/** Build the compact “what filters are applied” text. */
function buildVisibleFiltersSummary(filters) {
    const current = normalizeOrderFilters(filters);
    const parts = [];

    parts.push(
        `сортиране: ${SORT_BY_LABELS[current.sortBy] || current.sortBy} (${formatSortDirectionLabel(
            current.sortBy,
            current.sortDir
        )})`
    );

    const types = [];
    if (current.includeOrder) {
        types.push("поръчки");
    }
    if (current.includeOffer) {
        types.push("оферти");
    }
    parts.push(types.length ? `тип: ${types.join(" + ")}` : "тип: няма");

    if (current.start || current.end) {
        const startLabel = current.start ? formatFilterDateLabel(current.start) : "…";
        const endLabel = current.end ? formatFilterDateLabel(current.end) : "…";
        parts.push(`период: ${startLabel} – ${endLabel}`);
    }

    return parts.join(" · ");
}

/** Update the filter summary below the visible-items counter (only when non-default). */
function updateVisibleFiltersSummary(filters) {
    const summaryNode = document.getElementById("visible-items-filters");
    if (!summaryNode) {
        return;
    }

    const current = normalizeOrderFilters(filters);
    if (!filtersAreActive(current)) {
        summaryNode.textContent = "";
        summaryNode.classList.add("d-none");
        return;
    }

    summaryNode.textContent = buildVisibleFiltersSummary(current);
    summaryNode.classList.remove("d-none");
}

/** Show the direction options matching the selected sort field. */
function showSortDirectionPanel(sortBy) {
    const sortDirPanel = document.getElementById("dynamic-filter-sort-dir-panel");
    if (!sortDirPanel) {
        return;
    }

    sortDirPanel.querySelectorAll("[data-sort-dir-for]").forEach((panel) => {
        panel.classList.toggle("d-none", panel.dataset.sortDirFor !== sortBy);
    });
}

/** Sync filter controls to the given filter state (no refetch). */
function syncFilterControls(filters) {
    const current = normalizeOrderFilters(filters);

    const sortByInput = document.querySelector(
        `input[name="filter-sort-by"][value="${current.sortBy}"]`
    );
    if (sortByInput) {
        sortByInput.checked = true;
    }

    const sortDirInput = document.querySelector(
        `input[name="filter-sort-dir-${current.sortBy}"][value="${current.sortDir}"]`
    );
    if (sortDirInput) {
        sortDirInput.checked = true;
    }

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

    const category = document.querySelector('input[name="filter-category"]:checked');
    if (!category || category.value === "sort") {
        showSortDirectionPanel(current.sortBy);
    }

    updateFilterBadge(current);
    updateVisibleFiltersSummary(current);
}

/** Show the options panel for the selected filter category. */
function showFilterCategoryPanel(category) {
    document.querySelectorAll("[data-filter-panel]").forEach((panel) => {
        panel.classList.toggle("d-none", panel.dataset.filterPanel !== category);
    });

    const sortDirPanel = document.getElementById("dynamic-filter-sort-dir-panel");
    const calendarPanel = document.getElementById("dynamic-filter-calendar-panel");
    const root = document.getElementById("dynamic-orders-root");
    const filters = getFiltersForView(root?.dataset.currentView || "table");

    if (category === "sort") {
        if (sortDirPanel) {
            sortDirPanel.classList.remove("d-none");
        }
        if (calendarPanel) {
            calendarPanel.classList.add("d-none");
        }
        const dateTarget = document.querySelector('input[name="filter-date-target"]:checked');
        if (dateTarget) {
            dateTarget.checked = false;
        }
        showSortDirectionPanel(filters.sortBy);
        return;
    }

    if (sortDirPanel) {
        sortDirPanel.classList.add("d-none");
    }

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

/** Open the calendar column for start/end date editing. */
function openDateCalendar(target, filters) {
    const sortDirPanel = document.getElementById("dynamic-filter-sort-dir-panel");
    const calendarPanel = document.getElementById("dynamic-filter-calendar-panel");
    const calendarLabel = document.getElementById("dynamic-filter-calendar-label");
    const dateInput = document.getElementById("dynamic-filter-date-input");
    if (!calendarPanel || !dateInput) {
        return;
    }

    if (sortDirPanel) {
        sortDirPanel.classList.add("d-none");
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

/** Persist filters, clear cached rows, and refetch the active view. */
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
    syncFilterControls(filters);
    updateVisibleItemsCounter(0, viewName);

    const { generation } = beginOrdersRender(viewName);
    fetchAndRenderOrders({ forceRefresh: true, viewName, generation });
}

/** Reset filters for the active view back to defaults. */
function resetFiltersAndRefresh() {
    applyFiltersAndRefresh(getDefaultOrderFilters());
}

/** Wire filter UI events (category panels + immediate filter applies). */
function setupDynamicFilters() {
    const filterRoot = document.getElementById("collapseExample");
    if (!filterRoot || filterRoot.dataset.filtersBound === "1") {
        return;
    }
    filterRoot.dataset.filtersBound = "1";

    const root = document.getElementById("dynamic-orders-root");
    const initialView = root?.dataset.currentView || "table";
    syncFilterControls(getFiltersForView(initialView));
    showFilterCategoryPanel("sort");

    filterRoot.querySelectorAll('input[name="filter-category"]').forEach((input) => {
        input.addEventListener("change", () => {
            if (input.checked) {
                showFilterCategoryPanel(input.value);
            }
        });
    });

    filterRoot.querySelectorAll('input[name="filter-sort-by"]').forEach((input) => {
        input.addEventListener("change", () => {
            if (!input.checked) {
                return;
            }
            showSortDirectionPanel(input.value);
            applyFiltersAndRefresh({ sortBy: input.value });
        });
    });

    filterRoot.querySelectorAll("[data-sort-dir]").forEach((input) => {
        input.addEventListener("change", () => {
            if (input.checked) {
                applyFiltersAndRefresh({ sortDir: input.value });
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
            const sortCategory = document.getElementById("filter-cat-sort");
            if (sortCategory) {
                sortCategory.checked = true;
                showFilterCategoryPanel("sort");
            }
        });
    }
}

/** Start a new render generation for the given view. */
function beginOrdersRender(viewName) {
    ordersRenderGeneration += 1;
    return { generation: ordersRenderGeneration, viewName };
}

/** True when this async render is still the active one for the expected view. */
function isOrdersRenderCurrent(generation, viewName) {
    if (generation !== ordersRenderGeneration) {
        return false;
    }
    const root = document.getElementById("dynamic-orders-root");
    if (!root || root.dataset.currentView !== viewName) {
        return false;
    }
    const tableBody = document.getElementById("dynamic-orders-body");
    return Boolean(tableBody && tableBody.isConnected && tableBody.dataset.view === viewName);
}

/** Live tbody for a view, or null if the DOM has moved on. */
function getLiveOrdersBody(viewName) {
    const tableBody = document.getElementById("dynamic-orders-body");
    if (!tableBody || !tableBody.isConnected || tableBody.dataset.view !== viewName) {
        return null;
    }
    return tableBody;
}

/** Reject cache entries polluted by a cross-view race (wrong app URL in rows). */
function cacheMatchesView(rowsHtml, viewName) {
    if (!rowsHtml) {
        return true;
    }
    /** Only fail when the other app's row URLs are present. */
    if (viewName === "table" && rowsHtml.includes("/vitrine/view_vitrine/")) {
        return false;
    }
    if (viewName === "vitrine" && rowsHtml.includes("/table/viewOrder/")) {
        return false;
    }
    return true;
}

/** Build loading-state row HTML while async request is in progress. */
function buildLoadingRow(colspan) {
    return `
        <tr>
            <td colspan="${colspan}" class="text-center py-4">
                <div class="d-inline-flex align-items-center gap-2">
                    <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
                    <span>Зареждане...</span>
                </div>
            </td>
        </tr>
    `;
}

/** Build error-state row HTML with retry action. */
function buildErrorRow(colspan) {
    return `
        <tr>
            <td colspan="${colspan}" class="text-center py-4">
                <div class="text-danger mb-2">Грешка при зареждане на поръчките.</div>
                <button type="button" class="btn btn-sm btn-outline-primary" id="dynamic-orders-retry">Опитай отново</button>
            </td>
        </tr>
    `;
}

/** Build empty-state row HTML when endpoint returns no rows. */
function buildEmptyRow(colspan) {
    return `
        <tr>
            <td colspan="${colspan}" class="text-center text-muted py-4">Няма поръчки за показване.</td>
        </tr>
    `;
}

/** Footer status: loading more spinner. */
function buildLoadingMoreStatus() {
    return `
        <div class="d-inline-flex align-items-center gap-2 text-muted">
            <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
            <span>Зареждане...</span>
        </div>
    `;
}

/** Footer status: load-more error with retry. */
function buildLoadMoreErrorStatus() {
    return `
        <div class="text-danger mb-2">Грешка при зареждане на още поръчки.</div>
        <button type="button" class="btn btn-sm btn-outline-primary" id="dynamic-orders-load-more-retry">Опитай отново</button>
    `;
}

/** Footer status: end of list. */
function buildEndOfListStatus() {
    return `<div class="text-muted">Това са всички поръчки</div>`;
}

/** Toggle active nav tab based on selected dynamic view. */
function updateDynamicNavigation(viewName) {
    const navButtons = document.querySelectorAll("[data-dynamic-view]");
    navButtons.forEach((button) => {
        const isActive = button.dataset.dynamicView === viewName;
        button.classList.toggle("active", isActive);
    });
}

/** Point "new order" button to table/vitrine create URL. */
function updateNewOrderLink(viewName) {
    const newOrderLink = document.getElementById("dynamic-new-order-link");
    if (!newOrderLink) {
        return;
    }

    const tableUrl = newOrderLink.dataset.tableUrl;
    const vitrineUrl = newOrderLink.dataset.vitrineUrl;
    newOrderLink.href = viewName === "vitrine" ? vitrineUrl : tableUrl;
}

/** Get pre-rendered shell markup template for selected view. */
function getShellMarkup(viewName) {
    const template = document.getElementById(`dynamic-${viewName}-shell-template`);
    if (!template) {
        return "";
    }
    return template.innerHTML;
}

/** Ensure a stylesheet is attached once in document head. */
function ensureStylesheetLink(id, href) {
    if (!href || document.getElementById(id)) {
        return;
    }
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.type = "text/css";
    link.href = href;
    document.head.appendChild(link);
}

/** Lazy-load vitrine CSS only when vitrine view is needed. */
function ensureVitrineStylesIfNeeded(viewName) {
    if (viewName !== "vitrine") {
        return;
    }
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }

    ensureStylesheetLink("dynamic-vitrine-css-vitrines", root.dataset.vitrineCssVitrines);
    ensureStylesheetLink("dynamic-vitrine-css-holes", root.dataset.vitrineCssHoles);
    ensureStylesheetLink("dynamic-vitrine-css-modal", root.dataset.vitrineCssModal);
}

/** Fade out currently rendered rows before replacing tbody content. */
async function fadeOutRows(tableBody) {
    const rows = resolveFadeTargetRows(tableBody);
    if (!rows.length) {
        return;
    }

    rows.forEach((row) => {
        row.style.transition = "opacity 100ms ease-out";
        row.style.opacity = "0";
    });

    await new Promise((resolve) => window.setTimeout(resolve, 110));
}

/** Pick rows to animate. Prefer visible order rows so hidden detail rows are not staggered. */
function resolveFadeTargetRows(rowsOrBody) {
    if (Array.isArray(rowsOrBody)) {
        const visible = rowsOrBody.filter((row) => row.classList.contains("visibleRows"));
        return visible.length ? visible : rowsOrBody;
    }
    const visible = Array.from(rowsOrBody.querySelectorAll("tr.visibleRows"));
    if (visible.length) {
        return visible;
    }
    return Array.from(rowsOrBody.querySelectorAll("tr"));
}

/** Fade in rows with CSS transition-delay in one paint instead of per-row timers. */
function fadeInRows(rowsOrBody) {
    const targetRows = resolveFadeTargetRows(rowsOrBody);
    if (!targetRows.length) {
        return;
    }

    targetRows.forEach((row) => {
        row.style.transition = "none";
        row.style.opacity = "0";
        row.style.transform = "translateY(4px)";
        row.style.willChange = "opacity, transform";
    });

    /** Force style flush so the hidden state is painted before transitions run. */
    void targetRows[0].offsetHeight;

    targetRows.forEach((row, index) => {
        const delayMs = index * 12;
        row.style.transition = `opacity 180ms ease-in ${delayMs}ms, transform 180ms ease-in ${delayMs}ms`;
    });

    window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
            targetRows.forEach((row) => {
                row.style.opacity = "1";
                row.style.transform = "translateY(0)";
            });
        });
    });

    targetRows.forEach((row, index) => {
        const cleanupDelay = index * 12 + 200;
        window.setTimeout(() => {
            row.style.transition = "";
            row.style.transform = "";
            row.style.willChange = "";
        }, cleanupDelay);
    });
}

/** Bind row click handlers immediately (keep this before animation). */
function bindOrderRowHandlers() {
    if (typeof handle_orders === "function") {
        handle_orders();
    }
}

/** Heavier post-render work that can wait until the fade has started. */
function finalizeRenderedRows(viewName, generation) {
    if (!isOrdersRenderCurrent(generation, viewName)) {
        return;
    }
    if (typeof syncFrameHeights === "function") {
        syncFrameHeights();
    }
    restoreCachedOrderDetails(viewName);
    /** Re-open after details are in the DOM so expand height is measured correctly. */
    window.requestAnimationFrame(() => {
        if (!isOrdersRenderCurrent(generation, viewName)) {
            return;
        }
        restoreOpenRows(viewName);
    });
}

/** Run light setup now; defer layout/details so fade-in stays smooth. */
function setupRenderedRows(viewName, generation, { deferHeavyWork = false } = {}) {
    if (!isOrdersRenderCurrent(generation, viewName)) {
        return;
    }
    bindOrderRowHandlers();

    if (!deferHeavyWork) {
        finalizeRenderedRows(viewName, generation);
        return;
    }

    window.requestAnimationFrame(() => {
        window.setTimeout(() => finalizeRenderedRows(viewName, generation), 0);
    });
}

/** Rehydrate cached hidden-row order details and prevent re-fetching them. */
function restoreCachedOrderDetails(viewName) {
    const cached = viewOrdersCache.get(viewName);
    if (!cached || !cached.orderDetails) {
        return;
    }

    Object.entries(cached.orderDetails).forEach(([orderId, detailsHtml]) => {
        const hiddenTable = document.getElementById(`hidden-table-${orderId}`);
        const hiddenRow = document.getElementById(`hidden-row-${orderId}`);
        if (!hiddenTable || !hiddenRow || !detailsHtml) {
            return;
        }
        hiddenTable.innerHTML = detailsHtml;
        hiddenRow.classList.add("fetch-prevent");
    });

    if (typeof handle_orders_properties === "function") {
        handle_orders_properties();
    }
    if (typeof handle_orders_history === "function") {
        handle_orders_history();
    }
}

/** True when a hidden row looks expanded in the DOM. */
function isHiddenRowVisuallyOpen(hiddenRow) {
    if (!hiddenRow) {
        return false;
    }
    if (hiddenRow.classList.contains("is-open") || hiddenRow.classList.contains("orderClicked")) {
        return true;
    }
    return hiddenRow.style.display === "block";
}

/** Sync JS open flag with restored DOM so the next click folds instead of re-opening. */
function syncHiddenRowOpenState(hiddenRow, visibleRow, isOpen) {
    if (!hiddenRow) {
        return;
    }
    hiddenRow._isOpen = Boolean(isOpen);
    hiddenRow._isClosing = false;
    hiddenRow._isAnimating = false;
    if (isOpen) {
        hiddenRow.classList.add("is-open", "orderClicked");
        hiddenRow.classList.remove("is-closing");
        hiddenRow.style.display = "block";
        if (!hiddenRow.style.height || hiddenRow.style.height === "0px") {
            hiddenRow.style.height = "auto";
        }
        if (visibleRow) {
            visibleRow.classList.add("rowSelected");
        }
        return;
    }
    hiddenRow.classList.remove("is-open", "orderClicked", "is-closing");
    hiddenRow.style.display = "none";
    hiddenRow.style.height = "0px";
    if (visibleRow) {
        visibleRow.classList.remove("rowSelected");
    }
}

/** Collapse any open markup baked into cached HTML before rehydrating open rows. */
function resetCachedRowsOpenMarkup(tableBody) {
    if (!tableBody) {
        return;
    }
    tableBody.querySelectorAll(".hiddenRows").forEach((hiddenRow) => {
        syncHiddenRowOpenState(hiddenRow, null, false);
    });
    tableBody.querySelectorAll(".visibleRows.rowSelected").forEach((visibleRow) => {
        visibleRow.classList.remove("rowSelected");
    });
}

/** Capture currently expanded row ids for a specific view before switching away. */
function captureOpenRows(viewName) {
    if (!viewName) {
        return;
    }
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry) {
        return;
    }

    /** Prefer is-open/orderClicked/_isOpen/display:block; is-open is only set on transitionend. */
    const openRowIds = Array.from(document.querySelectorAll(".hiddenRows"))
        .filter((hiddenRow) => {
            if (hiddenRow._isOpen || isHiddenRowVisuallyOpen(hiddenRow)) {
                return true;
            }
            return false;
        })
        .map((hiddenRow) => hiddenRow.id.replace("hidden-row-", ""))
        .filter(Boolean);

    cacheEntry.openRowIds = openRowIds;
    viewOrdersCache.set(viewName, cacheEntry);
}

/** Save window scroll position for the active view. */
function captureScrollPosition(viewName) {
    if (!viewName) {
        return;
    }
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry) {
        return;
    }
    cacheEntry.scrollY = window.scrollY;
    viewOrdersCache.set(viewName, cacheEntry);
}

/** Restore previously saved scroll position for a view. */
function restoreScrollPosition(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry || typeof cacheEntry.scrollY !== "number") {
        return;
    }
    window.requestAnimationFrame(() => {
        window.scrollTo(0, cacheEntry.scrollY);
    });
}

/** Re-open previously expanded rows from cache without refetching details. */
function restoreOpenRows(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry || !Array.isArray(cacheEntry.openRowIds) || !cacheEntry.openRowIds.length) {
        return;
    }

    cacheEntry.openRowIds.forEach((rowId) => {
        const visibleRow = document.getElementById(rowId);
        const hiddenRow = document.getElementById(`hidden-row-${rowId}`);
        if (!visibleRow || !hiddenRow) {
            return;
        }
        if (hiddenRow._isOpen) {
            return;
        }
        /** Cached HTML may already look open; sync flag so the next click folds. */
        if (isHiddenRowVisuallyOpen(hiddenRow)) {
            syncHiddenRowOpenState(hiddenRow, visibleRow, true);
            return;
        }
        /** Call open directly: more reliable than synthetic click after rebind. */
        if (typeof openHiddenRow === "function") {
            openHiddenRow(hiddenRow, rowId, visibleRow);
        } else {
            visibleRow.click();
        }
    });
}

/** Update or clear the footer status area under the table. */
function setFooterStatus(html) {
    const statusNode = document.getElementById("dynamic-orders-status");
    if (!statusNode) {
        return;
    }
    statusNode.innerHTML = html || "";
}

/** Persist current tbody + pagination state into the per-view cache. */
function updateViewCache(viewName, patch) {
    const previous = viewOrdersCache.get(viewName) || {
        rowsHtml: "",
        visibleItems: 0,
        orderDetails: {},
        openRowIds: [],
        nextCursor: null,
        hasMore: false,
        scrollY: 0,
        filters: getDefaultOrderFilters(),
    };
    viewOrdersCache.set(viewName, { ...previous, ...patch });
}

/** Disconnect previous infinite-scroll observer. */
function teardownInfiniteScroll() {
    if (infiniteScrollObserver) {
        infiniteScrollObserver.disconnect();
        infiniteScrollObserver = null;
    }
}

/** Observe the sentinel and load the next page when it enters the viewport. */
function setupInfiniteScroll(viewName, generation) {
    teardownInfiniteScroll();

    if (!isOrdersRenderCurrent(generation, viewName)) {
        return;
    }

    const cacheEntry = viewOrdersCache.get(viewName);
    const sentinel = document.getElementById("dynamic-orders-sentinel");
    if (!sentinel || !cacheEntry || !cacheEntry.hasMore) {
        if (cacheEntry && cacheEntry.visibleItems > 0 && !cacheEntry.hasMore) {
            setFooterStatus(buildEndOfListStatus());
        }
        return;
    }

    setFooterStatus("");
    infiniteScrollObserver = new IntersectionObserver(
        (entries) => {
            const entry = entries[0];
            if (!entry || !entry.isIntersecting || isLoadingMore) {
                return;
            }
            if (!isOrdersRenderCurrent(generation, viewName)) {
                teardownInfiniteScroll();
                return;
            }
            loadMoreOrders(viewName, generation);
        },
        {
            root: null,
            rootMargin: "200px 0px",
            threshold: 0,
        }
    );
    infiniteScrollObserver.observe(sentinel);
}

/** Build paginated endpoint URL with active filters and optional cursor. */
function buildOrdersUrl(endpoint, cursor, viewName = null) {
    const url = new URL(endpoint, window.location.origin);
    url.searchParams.set("limit", "50");

    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    const filters = getFiltersForView(resolvedView);

    url.searchParams.set("sort_by", filters.sortBy || "date");
    url.searchParams.set("sort", filters.sortDir || "desc");
    if (filters.start) {
        url.searchParams.set("start", filters.start);
    }
    if (filters.end) {
        url.searchParams.set("end", filters.end);
    }

    if (filters.includeOrder) {
        url.searchParams.append("order_type", "order");
    }
    if (filters.includeOffer) {
        url.searchParams.append("order_type", "offer");
    }
    if (!filters.includeOrder && !filters.includeOffer) {
        // Explicit empty selection so the backend returns no rows (not the default type).
        url.searchParams.append("order_type", "");
    }

    if (cursor) {
        url.searchParams.set("cursor", cursor);
    }
    return url.toString();
}

/** Append the next page of rows for infinite scroll. */
async function loadMoreOrders(viewName, generation) {
    if (!isOrdersRenderCurrent(generation, viewName) || isLoadingMore) {
        return;
    }

    const tableBody = getLiveOrdersBody(viewName);
    if (!tableBody) {
        return;
    }

    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry || !cacheEntry.hasMore || !cacheEntry.nextCursor) {
        setFooterStatus(cacheEntry && cacheEntry.visibleItems > 0 ? buildEndOfListStatus() : "");
        teardownInfiniteScroll();
        return;
    }

    const endpoint = tableBody.dataset.endpoint;
    if (!endpoint || tableBody.dataset.view !== viewName) {
        return;
    }

    isLoadingMore = true;
    setFooterStatus(buildLoadingMoreStatus());

    try {
        const response = await fetch(buildOrdersUrl(endpoint, cacheEntry.nextCursor, viewName), {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} ${response.statusText}`);
        }

        const payload = await response.json();
        if (!isOrdersRenderCurrent(generation, viewName)) {
            return;
        }

        const liveBody = getLiveOrdersBody(viewName);
        if (!liveBody) {
            return;
        }

        const rowsHtml = payload.rows_html || "";
        const pageCount = Number.parseInt(payload.visible_items, 10) || 0;
        const hasMore = Boolean(payload.has_more);
        const nextCursor = payload.next_cursor || null;

        if (!rowsHtml) {
            updateViewCache(viewName, { hasMore: false, nextCursor: null });
            setFooterStatus(buildEndOfListStatus());
            teardownInfiniteScroll();
            return;
        }

        const template = document.createElement("tbody");
        template.innerHTML = rowsHtml;
        const newRows = Array.from(template.children);
        newRows.forEach((row) => liveBody.appendChild(row));

        const visibleItems = (cacheEntry.visibleItems || 0) + pageCount;
        updateViewCache(viewName, {
            rowsHtml: liveBody.innerHTML,
            visibleItems,
            hasMore,
            nextCursor,
        });
        updateVisibleItemsCounter(visibleItems, viewName);
        setupRenderedRows(viewName, generation, { deferHeavyWork: true });
        fadeInRows(newRows);

        if (hasMore) {
            setFooterStatus("");
        } else {
            setFooterStatus(buildEndOfListStatus());
            teardownInfiniteScroll();
        }
    } catch (error) {
        if (!isOrdersRenderCurrent(generation, viewName)) {
            return;
        }
        console.error(error);
        setFooterStatus(buildLoadMoreErrorStatus());
        const retryButton = document.getElementById("dynamic-orders-load-more-retry");
        if (retryButton) {
            retryButton.addEventListener(
                "click",
                () => {
                    setFooterStatus("");
                    loadMoreOrders(viewName, generation);
                },
                { once: true }
            );
        }
    } finally {
        if (generation === ordersRenderGeneration) {
            isLoadingMore = false;
        }
    }
}

/** Render cached rows immediately for already-loaded view content. */
async function renderCachedRowsIfAvailable(tableBody, viewName, colspan, generation) {
    const cached = viewOrdersCache.get(viewName);
    if (!cached || !cached.rowsHtml) {
        return false;
    }

    /** Drop cache polluted by an earlier cross-view race and refetch. */
    if (!cacheMatchesView(cached.rowsHtml, viewName)) {
        viewOrdersCache.delete(viewName);
        return false;
    }

    await fadeOutRows(tableBody);
    if (!isOrdersRenderCurrent(generation, viewName)) {
        return true;
    }

    const liveBody = getLiveOrdersBody(viewName);
    if (!liveBody) {
        return true;
    }

    liveBody.innerHTML = cached.rowsHtml;
    /** Strip any open markup baked into cached HTML, then re-open via openRowIds. */
    resetCachedRowsOpenMarkup(liveBody);
    updateVisibleItemsCounter(cached.visibleItems || 0, viewName);
    setupRenderedRows(viewName, generation, { deferHeavyWork: true });
    fadeInRows(liveBody);
    setupInfiniteScroll(viewName, generation);
    restoreScrollPosition(viewName);
    return true;
}

/** Fetch first page from endpoint and render loading/success/error states. */
async function fetchAndRenderOrders({ forceRefresh = false, viewName = null, generation = null } = {}) {
    const tableBody = document.getElementById("dynamic-orders-body");
    if (!tableBody) {
        return;
    }

    const resolvedView = viewName || tableBody.dataset.view || "table";
    const endpoint = tableBody.dataset.endpoint;
    const colspan = Number.parseInt(tableBody.dataset.colspan || "10", 10);
    if (!endpoint || tableBody.dataset.view !== resolvedView) {
        return;
    }

    const renderGeneration =
        generation == null ? beginOrdersRender(resolvedView).generation : generation;

    teardownInfiniteScroll();
    isLoadingMore = false;

    if (!forceRefresh) {
        const renderedFromCache = await renderCachedRowsIfAvailable(
            tableBody,
            resolvedView,
            colspan,
            renderGeneration
        );
        if (renderedFromCache) {
            return;
        }
    }

    if (!isOrdersRenderCurrent(renderGeneration, resolvedView)) {
        return;
    }

    await fadeOutRows(tableBody);
    if (!isOrdersRenderCurrent(renderGeneration, resolvedView)) {
        return;
    }

    const loadingBody = getLiveOrdersBody(resolvedView);
    if (!loadingBody) {
        return;
    }
    loadingBody.innerHTML = buildLoadingRow(colspan);
    setFooterStatus("");

    try {
        const response = await fetch(buildOrdersUrl(endpoint, null, resolvedView), {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} ${response.statusText}`);
        }

        const payload = await response.json();
        const rowsHtml = payload.rows_html || "";
        const visibleItems = Number.parseInt(payload.visible_items, 10) || 0;
        const hasMore = Boolean(payload.has_more);
        const nextCursor = payload.next_cursor || null;
        const previousCache = viewOrdersCache.get(resolvedView);

        /** Keep payload for this view even after switch; do not wipe openRowIds/scrollY. */
        updateViewCache(resolvedView, {
            rowsHtml,
            visibleItems,
            hasMore,
            nextCursor,
            orderDetails: previousCache?.orderDetails || {},
        });

        if (!isOrdersRenderCurrent(renderGeneration, resolvedView)) {
            return;
        }

        const liveBody = getLiveOrdersBody(resolvedView);
        if (!liveBody) {
            return;
        }

        liveBody.innerHTML = rowsHtml || buildEmptyRow(colspan);
        updateVisibleItemsCounter(visibleItems, resolvedView);
        setupRenderedRows(resolvedView, renderGeneration, { deferHeavyWork: true });
        fadeInRows(liveBody);

        if (rowsHtml) {
            setupInfiniteScroll(resolvedView, renderGeneration);
        } else {
            setFooterStatus("");
        }
    } catch (error) {
        if (!isOrdersRenderCurrent(renderGeneration, resolvedView)) {
            return;
        }
        console.error(error);
        const liveBody = getLiveOrdersBody(resolvedView);
        if (!liveBody) {
            return;
        }
        liveBody.innerHTML = buildErrorRow(colspan);
        fadeInRows(liveBody);
        updateVisibleItemsCounter(0, resolvedView);
        setFooterStatus("");

        const retryButton = document.getElementById("dynamic-orders-retry");
        if (retryButton) {
            retryButton.addEventListener(
                "click",
                () => fetchAndRenderOrders({ forceRefresh: true, viewName: resolvedView }),
                { once: true }
            );
        }
    }
}

/** Switch between table/vitrine shells and trigger new async load. */
function switchDynamicView(viewName) {
    const root = document.getElementById("dynamic-orders-root");
    const container = document.getElementById("dynamic-orders-table-container");
    if (!root || !container) {
        return;
    }

    const previousViewName = root.dataset.currentView;
    captureOpenRows(previousViewName);
    captureScrollPosition(previousViewName);
    teardownInfiniteScroll();

    const { generation } = beginOrdersRender(viewName);
    root.dataset.currentView = viewName;
    updateDynamicNavigation(viewName);
    updateNewOrderLink(viewName);
    updateVisibleItemsCounter(0, viewName);
    ensureVitrineStylesIfNeeded(viewName);

    container.innerHTML = getShellMarkup(viewName);
    syncFilterControls(getFiltersForView(viewName));
    fetchAndRenderOrders({ viewName, generation });
}

/** Initialize dynamic page behavior after DOM is ready. */
document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }

    ensureVitrineStylesIfNeeded(root.dataset.currentView);
    setupDynamicFilters();
    fetchAndRenderOrders({ viewName: root.dataset.currentView || "table" });

    const navButtons = document.querySelectorAll("[data-dynamic-view]");
    navButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const selectedView = button.dataset.dynamicView;
            const currentView = root.dataset.currentView;
            if (!selectedView || selectedView === currentView) {
                return;
            }
            switchDynamicView(selectedView);
        });
    });
});
