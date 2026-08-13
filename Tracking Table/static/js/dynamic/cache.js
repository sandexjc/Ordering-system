/*
 * dynamic/cache.js
 * ----------------
 * Per-view cache helpers: merge patches, restore details, open rows, scroll position.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - dynamic/state.js
 *   - dynamic/filters.js → getDefaultOrderFilters
 * Runtime depends on:
 *   - orders/row-expand/open-close.js → openHiddenRow
 *   - orders/details/spinner.js → set_hidden_row_close_visible
 *   - orders/actions → handle_orders_properties, handle_orders_history
 */

/**
 * Rehydrate cached hidden-row order details and prevent re-fetching them.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
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
        if (typeof set_hidden_row_close_visible === "function") {
            set_hidden_row_close_visible(orderId, true);
        }
    });

    if (typeof handle_orders_properties === "function") {
        handle_orders_properties();
    }
    if (typeof handle_orders_history === "function") {
        handle_orders_history();
    }
}

/** True when a hidden row looks expanded in the DOM.
 * @param {*} hiddenRow - Expanded detail row element.
 * @returns {boolean}
 */
function isHiddenRowVisuallyOpen(hiddenRow) {
    if (!hiddenRow) {
        return false;
    }
    if (hiddenRow.classList.contains("is-open") || hiddenRow.classList.contains("orderClicked")) {
        return true;
    }
    return hiddenRow.style.display === "block";
}

/** Sync JS open flag with restored DOM so the next click folds instead of re-opening.
 * @param {*} hiddenRow - Expanded detail row element.
 * @param {*} visibleRow - Visible order row element.
 * @param {*} isOpen - Whether the row should appear open.
 * @returns {void}
 */
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

/** Collapse any open markup baked into cached HTML before rehydrating open rows.
 * @param {*} tableBody - Orders <tbody> element.
 * @returns {void}
 */
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

/** Capture currently expanded row ids for a specific view before switching away.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
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

/** Save window scroll position for the active view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
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

/** Restore previously saved scroll position for a view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function restoreScrollPosition(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry || typeof cacheEntry.scrollY !== "number") {
        return;
    }
    window.requestAnimationFrame(() => {
        window.scrollTo(0, cacheEntry.scrollY);
    });
}

/** Re-open previously expanded rows from cache without refetching details.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
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

/**
 * updateViewCache
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @param {*} patch - Partial filter or cache fields to merge.
 * @returns {void}
 */
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
        searchQuery: "",
    };
    viewOrdersCache.set(viewName, { ...previous, ...patch });
}
