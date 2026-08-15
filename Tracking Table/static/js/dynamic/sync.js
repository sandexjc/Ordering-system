/*
 * dynamic/sync.js
 * ---------------
 * Short-poll live updates for already-loaded table / vitrine boards.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html (after fetch.js, before page.js)
 *
 * Depends on (load order):
 *   - dynamic/state.js
 *   - dynamic/filters.js → getFiltersForView, getOrdersEndpointForView, updateVisibleItemsCounter
 *   - dynamic/search.js  → getSearchForView, highlightSearchInOrders
 *   - dynamic/cache.js   → updateViewCache, captureLiveRowsHtml, isHiddenRowVisuallyOpen
 *   - dynamic/fetch.js   → buildOrdersUrl, fetchAndRenderOrders, getLiveOrdersBody
 * Runtime depends on:
 *   - orders/actions/progress-delete.js → remove_deleted_order_row
 *   - orders/details/fetch.js           → get_order
 *   - orders/row-expand/bind-rows.js    → handle_orders
 *   - vitrine/js/virtual_rows.js        → syncFrameHeights (optional)
 */

/**
 * Remember a local mutation so this tab does not purple-highlight its own click.
 *
 * @param {string|number} orderId - Order / vitrine id.
 * @returns {void}
 */
function rememberLocalOrderMutation(orderId)
{
    if (orderId == null || orderId === "") {
        return;
    }
    const key = String(orderId);
    recentLocalOrderMutations.set(key, Date.now());
    const row = typeof getLiveVisibleOrderRow === "function"
        ? getLiveVisibleOrderRow(key)
        : document.querySelector('tr.visibleRows[data-row="' + key + '"]');
    if (row) {
        row.setAttribute("data-updated-at", String(Date.now() / 1000));
    }
}

/**
 * True when this tab mutated the row and we have not yet consumed the echo.
 *
 * @param {string|number} orderId - Order / vitrine id.
 * @returns {boolean}
 */
function isRecentLocalOrderMutation(orderId)
{
    const stamped = recentLocalOrderMutations.get(String(orderId));
    if (stamped == null) {
        return false;
    }
    if (Date.now() - stamped > LOCAL_MUTATION_SKIP_MS) {
        recentLocalOrderMutations.delete(String(orderId));
        return false;
    }
    return true;
}

/**
 * Drop the local-echo marker after the matching sync payload is handled.
 *
 * @param {string|number} orderId - Order / vitrine id.
 * @returns {void}
 */
function consumeLocalOrderMutation(orderId)
{
    recentLocalOrderMutations.delete(String(orderId));
}

/**
 * Views that already have a loaded list cache this session.
 *
 * @returns {string[]}
 */
function getLoadedSyncViewNames()
{
    const names = [];
    viewOrdersCache.forEach((cacheEntry, viewName) => {
        if (cacheEntry && cacheEntry.watermark) {
            names.push(viewName);
        }
    });
    return names;
}

/**
 * Build the sync GET URL for a view (same filters as the list, plus since).
 *
 * @param {string} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {string|null}
 */
function buildSyncUrl(viewName)
{
    const endpoint = typeof getOrdersEndpointForView === "function"
        ? getOrdersEndpointForView(viewName)
        : null;
    if (!endpoint || typeof buildOrdersUrl !== "function") {
        return null;
    }
    const url = new URL(buildOrdersUrl(endpoint, null, viewName), window.location.origin);
    url.searchParams.set("sync", "1");
    const watermark = viewOrdersCache.get(viewName)?.watermark;
    if (watermark) {
        url.searchParams.set("since", watermark);
    }
    return url.toString();
}

/**
 * Parse list HTML into summary + hidden-row pairs.
 *
 * @param {string} html - rows_html from the server.
 * @returns {Array<{id: string, summary: HTMLTableRowElement, hidden: HTMLTableRowElement|null}>}
 */
function parseOrderRowPairs(html)
{
    const tbody = document.createElement("tbody");
    tbody.innerHTML = html || "";
    const pairs = [];
    const children = Array.from(tbody.children);
    for (let index = 0; index < children.length; index += 1) {
        const row = children[index];
        if (!row.classList || !row.classList.contains("visibleRows")) {
            continue;
        }
        const next = children[index + 1];
        const hidden = next && !next.classList.contains("visibleRows") ? next : null;
        pairs.push({
            id: String(row.getAttribute("data-row") || row.id || ""),
            summary: row,
            hidden: hidden,
        });
    }
    return pairs;
}

/**
 * Summary rows currently in a tbody (live or detached cache).
 *
 * @param {HTMLElement} tbody - Orders tbody.
 * @returns {HTMLTableRowElement[]}
 */
function getLoadedSummaryRows(tbody)
{
    if (!tbody) {
        return [];
    }
    return Array.from(tbody.querySelectorAll("tr.visibleRows"));
}

/**
 * Sort tuple for the active sort field.
 *
 * @param {HTMLElement} row - Summary row.
 * @param {string} sortBy - "date" | "order_id" | "balance".
 * @returns {number[]}
 */
function getRowSortTuple(row, sortBy)
{
    const pk = Number.parseInt(row.getAttribute("data-pk") || row.getAttribute("data-row") || "0", 10) || 0;
    if (sortBy === "order_id") {
        return [pk, pk];
    }
    if (sortBy === "balance") {
        return [Number.parseFloat(row.getAttribute("data-sort-balance") || "0") || 0, pk];
    }
    const parsedDate = Date.parse(row.getAttribute("data-sort-date") || "");
    return [Number.isNaN(parsedDate) ? 0 : parsedDate, pk];
}

/**
 * Compare two sort tuples. Negative when `left` should appear before `right`.
 *
 * @param {number[]} left - Sort tuple.
 * @param {number[]} right - Sort tuple.
 * @param {string} sortDir - "asc" | "desc".
 * @returns {number}
 */
function compareSortTuples(left, right, sortDir)
{
    const direction = sortDir === "asc" ? 1 : -1;
    if (left[0] !== right[0]) {
        return left[0] < right[0] ? -1 * direction : 1 * direction;
    }
    if (left[1] !== right[1]) {
        return left[1] < right[1] ? -1 * direction : 1 * direction;
    }
    return 0;
}

/**
 * Numeric updated_at from a summary row (Unix seconds, possibly fractional).
 *
 * @param {HTMLElement} row - Summary row.
 * @returns {number}
 */
function rowUpdatedAtValue(row)
{
    const raw = (row && row.getAttribute("data-updated-at")) || "";
    const asNumber = Number.parseFloat(raw);
    if (raw !== "" && !Number.isNaN(asNumber)) {
        return asNumber;
    }
    const parsed = Date.parse(raw);
    return Number.isNaN(parsed) ? 0 : parsed / 1000;
}

/**
 * Stable summary signature that ignores local highlight / selection classes.
 *
 * @param {HTMLElement} row - Summary row.
 * @returns {string}
 */
function summarySyncSignature(row)
{
    if (!row) {
        return "";
    }
    const classes = Array.from(row.classList)
        .filter((name) => (
            name !== "is-sync-highlight"
            && name !== "rowSelected"
            && name !== "is-deleting"
        ))
        .sort()
        .join(" ");
    return classes + "\n" + row.innerHTML;
}

/**
 * True when incoming HTML/timestamp is newer than the row already on screen.
 *
 * @param {HTMLElement} existing - Current summary row.
 * @param {HTMLElement} incoming - Server summary row.
 * @returns {boolean}
 */
function shouldReplaceSummary(existing, incoming)
{
    const incomingAt = rowUpdatedAtValue(incoming);
    const existingAt = rowUpdatedAtValue(existing);
    if (incomingAt > existingAt) {
        return true;
    }
    if (incomingAt < existingAt) {
        return false;
    }
    return summarySyncSignature(existing) !== summarySyncSignature(incoming);
}

/**
 * True when the new row belongs among already-loaded rows (or the list is complete).
 *
 * @param {HTMLElement} newRow - Incoming summary row.
 * @param {HTMLElement} tbody - Target tbody.
 * @param {boolean} hasMore - Whether infinite scroll has another page.
 * @param {Object} filters - Active filters for this view.
 * @returns {boolean}
 */
function belongsInLoadedWindow(newRow, tbody, hasMore, filters)
{
    const loaded = getLoadedSummaryRows(tbody);
    if (!loaded.length) {
        return !hasMore;
    }
    const last = loaded[loaded.length - 1];
    const comparison = compareSortTuples(
        getRowSortTuple(newRow, filters.sortBy || "date"),
        getRowSortTuple(last, filters.sortBy || "date"),
        filters.sortDir || "desc"
    );
    if (comparison <= 0) {
        return true;
    }
    return !hasMore;
}

/**
 * Insert a summary+hidden pair into tbody at the current sort position.
 *
 * @param {HTMLElement} tbody - Target tbody.
 * @param {HTMLElement} summary - Visible row.
 * @param {HTMLElement|null} hidden - Hidden-row wrapper tr.
 * @param {Object} filters - Active filters for this view.
 * @returns {void}
 */
function insertRowPairInSortOrder(tbody, summary, hidden, filters)
{
    const emptyPlaceholder = tbody.querySelector("tr:not(.visibleRows)");
    if (!getLoadedSummaryRows(tbody).length && emptyPlaceholder) {
        tbody.innerHTML = "";
    }

    const loaded = getLoadedSummaryRows(tbody);
    let reference = null;
    for (let index = 0; index < loaded.length; index += 1) {
        const comparison = compareSortTuples(
            getRowSortTuple(summary, filters.sortBy || "date"),
            getRowSortTuple(loaded[index], filters.sortBy || "date"),
            filters.sortDir || "desc"
        );
        if (comparison < 0) {
            reference = loaded[index];
            break;
        }
    }

    if (reference) {
        tbody.insertBefore(summary, reference);
        if (hidden) {
            tbody.insertBefore(hidden, reference);
        }
        return;
    }
    tbody.appendChild(summary);
    if (hidden) {
        tbody.appendChild(hidden);
    }
}

/**
 * Remove a summary+hidden pair from a tbody if present.
 *
 * @param {HTMLElement} tbody - Target tbody.
 * @param {string} orderId - Order / vitrine id.
 * @returns {boolean} True when something was removed.
 */
function removeRowPairFromTbody(tbody, orderId)
{
    const id = String(orderId);
    const summary = tbody.querySelector('tr.visibleRows[data-row="' + id + '"]');
    const hiddenNode = tbody.querySelector('[id="hidden-row-' + id + '"]');
    const hiddenRow = hiddenNode ? hiddenNode.closest("tr") : null;
    let removed = false;
    if (summary) {
        summary.remove();
        removed = true;
    }
    if (hiddenRow) {
        hiddenRow.remove();
        removed = true;
    }
    return removed;
}

/**
 * Drop cached expanded-details HTML so the next expand refetches.
 *
 * @param {string} viewName - Dynamic view key.
 * @param {string} orderId - Order / vitrine id.
 * @returns {void}
 */
function dropCachedOrderDetails(viewName, orderId)
{
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry || !cacheEntry.orderDetails) {
        return;
    }
    delete cacheEntry.orderDetails[String(orderId)];
    viewOrdersCache.set(viewName, cacheEntry);
}

/**
 * Fade purple in on a remote insert/update. Stays until the user focuses or opens the row.
 *
 * @param {HTMLElement} row - Summary row.
 * @returns {void}
 */
function highlightSyncedRow(row)
{
    if (!row) {
        return;
    }
    const orderId = row.getAttribute("data-row") || row.id;
    if (isRecentLocalOrderMutation(orderId)) {
        return;
    }
    row.classList.add("is-sync-highlight");
}

/**
 * Remove the remote-update purple once the user has focused / opened / closed the row.
 *
 * @param {HTMLElement|null} row - Summary row.
 * @returns {void}
 */
function clearSyncedRowHighlight(row)
{
    if (!row) {
        return;
    }
    row.classList.remove("is-sync-highlight");
}

/**
 * Keep pending purple highlights after a cached board becomes visible (no auto-clear).
 *
 * @param {string} viewName - Dynamic view key.
 * @returns {void}
 */
function playPendingSyncHighlights(viewName)
{
    const tbody = typeof getLiveOrdersBody === "function" ? getLiveOrdersBody(viewName) : null;
    if (!tbody) {
        return;
    }
    tbody.querySelectorAll("tr.visibleRows.is-sync-highlight").forEach((row) => {
        highlightSyncedRow(row);
    });
}

/**
 * Rebind expand handlers and search marks after a live DOM patch.
 *
 * @param {string} viewName - Dynamic view key.
 * @returns {void}
 */
function afterLiveSyncDomPatch(viewName)
{
    if (typeof handle_orders === "function") {
        handle_orders();
    }
    if (typeof highlightSearchInOrders === "function") {
        highlightSearchInOrders(viewName);
    }
    if (typeof syncFrameHeights === "function") {
        syncFrameHeights();
    }
}

/**
 * Refresh expanded details unless a fetch is already in flight for this id.
 *
 * @param {string|number} orderId - Order / vitrine id.
 * @returns {void}
 */
function refreshOpenOrderDetailsIfNeeded(orderId)
{
    const key = String(orderId);
    const hiddenRow = document.getElementById("hidden-row-" + key);
    if (!hiddenRow) {
        return;
    }
    const isOpen = hiddenRow._isOpen === true
        || (typeof isHiddenRowVisuallyOpen === "function" && isHiddenRowVisuallyOpen(hiddenRow));
    if (!isOpen) {
        return;
    }
    if (ordersDetailsInFlight.has(key)) {
        return;
    }
    if (typeof get_order === "function") {
        get_order(key);
    }
}

/**
 * Replace only the summary row; keep the hidden-row tr (and any open details).
 *
 * @param {HTMLElement} tbody - Target tbody.
 * @param {object} pair - Parsed summary+hidden pair.
 * @param {boolean} isLive - Whether this tbody is on screen.
 * @returns {HTMLElement|null} The new summary row, or null.
 */
function replaceSummaryRow(tbody, pair, { highlight = true } = {})
{
    const existing = tbody.querySelector('tr.visibleRows[data-row="' + pair.id + '"]');
    if (!existing) {
        return null;
    }
    const wasSelected = existing.classList.contains("rowSelected");
    const wasHighlighted = existing.classList.contains("is-sync-highlight");
    existing.replaceWith(pair.summary);
    if (wasSelected) {
        pair.summary.classList.add("rowSelected");
    }
    if (highlight) {
        highlightSyncedRow(pair.summary);
    } else if (wasHighlighted) {
        pair.summary.classList.add("is-sync-highlight");
    }
    return pair.summary;
}

/**
 * Apply one deleted id to a tbody (live uses the existing delete animation).
 *
 * @param {string} viewName - Dynamic view key.
 * @param {HTMLElement} tbody - Target tbody.
 * @param {string|number} orderId - Order / vitrine id.
 * @param {boolean} isLive - Whether this tbody is on screen.
 * @returns {void}
 */
function applyDeletedOrder(viewName, tbody, orderId, isLive)
{
    dropCachedOrderDetails(viewName, orderId);
    if (isLive && typeof remove_deleted_order_row === "function") {
        const existing = tbody.querySelector('tr.visibleRows[data-row="' + String(orderId) + '"]');
        if (existing) {
            remove_deleted_order_row(orderId);
            return;
        }
    }
    removeRowPairFromTbody(tbody, orderId);
}

/**
 * Apply created/updated row pairs onto a tbody.
 *
 * @param {string} viewName - Dynamic view key.
 * @param {HTMLElement} tbody - Target tbody.
 * @param {object} pair - Parsed pair.
 * @param {boolean} isLive - Whether this tbody is on screen.
 * @param {boolean} hasMore - Infinite-scroll has more pages.
 * @param {Object} filters - Active filters.
 * @returns {void}
 */
function applyRowPair(viewName, tbody, pair, isLive, hasMore, filters)
{
    const localEcho = isLive && isRecentLocalOrderMutation(pair.id);
    const existing = tbody.querySelector('tr.visibleRows[data-row="' + pair.id + '"]');
    if (existing) {
        if (!shouldReplaceSummary(existing, pair.summary)) {
            const incomingAt = pair.summary.getAttribute("data-updated-at");
            if (incomingAt) {
                existing.setAttribute("data-updated-at", incomingAt);
            }
            if (localEcho) {
                consumeLocalOrderMutation(pair.id);
            }
            return;
        }
        dropCachedOrderDetails(viewName, pair.id);
        replaceSummaryRow(tbody, pair, { highlight: !localEcho });
        if (localEcho) {
            consumeLocalOrderMutation(pair.id);
        }
        if (isLive && !localEcho) {
            refreshOpenOrderDetailsIfNeeded(pair.id);
        }
        return;
    }
    if (!belongsInLoadedWindow(pair.summary, tbody, hasMore, filters)) {
        return;
    }
    dropCachedOrderDetails(viewName, pair.id);
    insertRowPairInSortOrder(tbody, pair.summary, pair.hidden, filters);
    if (!localEcho) {
        highlightSyncedRow(pair.summary);
    } else {
        consumeLocalOrderMutation(pair.id);
    }
}

/**
 * Persist patched HTML / counts back to the view cache.
 *
 * @param {string} viewName - Dynamic view key.
 * @param {HTMLElement} tbody - Source tbody.
 * @param {boolean} isLive - Whether to also update the on-screen counter.
 * @returns {void}
 */
function persistSyncedTbody(viewName, tbody, isLive)
{
    const visibleItems = getLoadedSummaryRows(tbody).length;
    updateViewCache(viewName, {
        rowsHtml: tbody.innerHTML,
        visibleItems: visibleItems,
    });
    if (isLive && typeof updateVisibleItemsCounter === "function") {
        updateVisibleItemsCounter(visibleItems, viewName);
    }
}

/**
 * Reload a hidden view's first page into cache only (no live DOM swap).
 *
 * @param {string} viewName - Dynamic view key.
 * @returns {Promise<void>}
 */
async function refetchOrdersIntoCache(viewName)
{
    const endpoint = typeof getOrdersEndpointForView === "function"
        ? getOrdersEndpointForView(viewName)
        : null;
    if (!endpoint || typeof buildOrdersUrl !== "function") {
        return;
    }
    const response = await fetch(buildOrdersUrl(endpoint, null, viewName), {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    });
    if (!response.ok) {
        throw new Error("HTTP " + response.status + " " + response.statusText);
    }
    const payload = await response.json();
    updateViewCache(viewName, {
        rowsHtml: payload.rows_html || "",
        visibleItems: Number.parseInt(payload.visible_items, 10) || 0,
        hasMore: Boolean(payload.has_more),
        nextCursor: payload.next_cursor || null,
        watermark: payload.watermark || viewOrdersCache.get(viewName)?.watermark,
        orderDetails: {},
    });
}

/**
 * Apply a sync payload to the live table or a cached tbody.
 *
 * @param {string} viewName - Dynamic view key.
 * @param {object} payload - Sync JSON.
 * @returns {Promise<void>}
 */
async function applySyncPayload(viewName, payload)
{
    if (payload.watermark) {
        updateViewCache(viewName, { watermark: payload.watermark });
    }

    const root = document.getElementById("dynamic-orders-root");
    const isLive = Boolean(root && root.dataset.currentView === viewName);
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry) {
        return;
    }

    if (payload.reload) {
        if (isLive && typeof fetchAndRenderOrders === "function") {
            await fetchAndRenderOrders({ forceRefresh: true, viewName: viewName });
            return;
        }
        await refetchOrdersIntoCache(viewName);
        return;
    }

    const deletedIds = Array.isArray(payload.deleted_ids) ? payload.deleted_ids : [];
    const pairs = parseOrderRowPairs(payload.rows_html || "");
    if (!deletedIds.length && !pairs.length) {
        return;
    }

    const filters = typeof getFiltersForView === "function"
        ? getFiltersForView(viewName)
        : { sortBy: "date", sortDir: "desc" };
    const hasMore = Boolean(cacheEntry.hasMore);
    let tbody = null;

    if (isLive) {
        tbody = typeof getLiveOrdersBody === "function" ? getLiveOrdersBody(viewName) : null;
    } else {
        tbody = document.createElement("tbody");
        tbody.innerHTML = cacheEntry.rowsHtml || "";
    }
    if (!tbody) {
        return;
    }

    deletedIds.forEach((orderId) => {
        applyDeletedOrder(viewName, tbody, orderId, isLive);
    });
    pairs.forEach((pair) => {
        if (!pair.id) {
            return;
        }
        applyRowPair(viewName, tbody, pair, isLive, hasMore, filters);
    });

    persistSyncedTbody(viewName, tbody, isLive);
    if (isLive) {
        afterLiveSyncDomPatch(viewName);
        if (typeof captureLiveRowsHtml === "function") {
            captureLiveRowsHtml(viewName);
        }
    }
}

/**
 * Poll one already-loaded view.
 *
 * @param {string} viewName - Dynamic view key.
 * @returns {Promise<void>}
 */
async function pollOrdersSyncForView(viewName)
{
    if (isOrdersListFetchInFlight || isLoadingMore) {
        return;
    }
    const url = buildSyncUrl(viewName);
    if (!url) {
        return;
    }
    const response = await fetch(url, {
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    });
    if (!response.ok) {
        throw new Error("HTTP " + response.status + " " + response.statusText);
    }
    const payload = await response.json();
    await applySyncPayload(viewName, payload);
}

/**
 * Poll every loaded board (current + cached other app).
 *
 * @returns {Promise<void>}
 */
async function pollOrdersSync()
{
    const root = document.getElementById("dynamic-orders-root");
    if (!root || document.visibilityState !== "visible") {
        return;
    }
    const viewNames = getLoadedSyncViewNames();
    if (!viewNames.length) {
        return;
    }
    for (let index = 0; index < viewNames.length; index += 1) {
        await pollOrdersSyncForView(viewNames[index]);
    }
}

/**
 * Schedule the next poll, with backoff after errors.
 *
 * @param {number} delayMs - Delay before the next tick.
 * @returns {void}
 */
function scheduleOrdersSync(delayMs)
{
    if (ordersSyncTimer) {
        window.clearTimeout(ordersSyncTimer);
    }
    ordersSyncTimer = window.setTimeout(runOrdersSyncTick, delayMs);
}

/**
 * One poll tick; reschedules itself.
 *
 * @returns {Promise<void>}
 */
async function runOrdersSyncTick()
{
    ordersSyncTimer = null;
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }
    if (document.visibilityState !== "visible") {
        return;
    }
    try {
        await pollOrdersSync();
        ordersSyncBackoffMs = ORDERS_SYNC_INTERVAL_MS;
    } catch (error) {
        console.error(error);
        ordersSyncBackoffMs = Math.min(ordersSyncBackoffMs * 2, 32000);
    }
    scheduleOrdersSync(ordersSyncBackoffMs);
}

/**
 * Start (or resume) live sync polling for the dynamic page.
 *
 * @returns {void}
 */
function setupOrdersLiveSync()
{
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }
    if (window.__ordersLiveSyncStarted) {
        return;
    }
    window.__ordersLiveSyncStarted = true;

    const clearHighlightFromEvent = (event) => {
        const row = event.target.closest("#dynamic-orders-root tr.visibleRows");
        if (row) {
            clearSyncedRowHighlight(row);
        }
    };
    root.addEventListener("focusin", clearHighlightFromEvent);
    root.addEventListener("pointerdown", clearHighlightFromEvent);

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible") {
            ordersSyncBackoffMs = ORDERS_SYNC_INTERVAL_MS;
            runOrdersSyncTick();
            return;
        }
        if (ordersSyncTimer) {
            window.clearTimeout(ordersSyncTimer);
            ordersSyncTimer = null;
        }
    });

    scheduleOrdersSync(ORDERS_SYNC_INTERVAL_MS);
}
