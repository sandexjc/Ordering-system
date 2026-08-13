/*
 * dynamic/fetch.js
 * ----------------
 * Render-generation guards, URL building, first-page fetch, infinite scroll / load-more.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - dynamic/state.js
 *   - dynamic/filters.js
 *   - dynamic/search.js
 *   - dynamic/cache.js
 *   - dynamic/render.js
 */

/**
 * Start a new render generation for the given view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {Object}
 */
function beginOrdersRender(viewName) {
    ordersRenderGeneration += 1;
    return { generation: ordersRenderGeneration, viewName };
}

/** True when this async render is still the active one for the expected view.
 * @param {*} generation - Render generation token from beginOrdersRender.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {boolean}
 */
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

/** Live tbody for a view, or null if the DOM has moved on.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {*}
 */
function getLiveOrdersBody(viewName) {
    const tableBody = document.getElementById("dynamic-orders-body");
    if (!tableBody || !tableBody.isConnected || tableBody.dataset.view !== viewName) {
        return null;
    }
    return tableBody;
}

/** Reject cache entries polluted by a cross-view race (wrong app URL in rows).
 * @param {*} rowsHtml - Cached or fetched rows HTML string.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {boolean}
 */
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

/**
 * teardownInfiniteScroll
 * @returns {void}
 */
function teardownInfiniteScroll() {
    if (infiniteScrollObserver) {
        infiniteScrollObserver.disconnect();
        infiniteScrollObserver = null;
    }
}

/** Observe the sentinel and load the next page when it enters the viewport.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @param {*} generation - Render generation token from beginOrdersRender.
 * @returns {void}
 */
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

/** Build paginated endpoint URL with active filters and optional cursor.
 * @param {*} endpoint - Orders list API endpoint URL.
 * @param {*} cursor - Pagination cursor, or null for first page.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {string}
 */
function buildOrdersUrl(endpoint, cursor, viewName = null) {
    const url = new URL(endpoint, window.location.origin);
    url.searchParams.set("limit", "50");

    const root = document.getElementById("dynamic-orders-root");
    const resolvedView = viewName || root?.dataset.currentView || "table";
    const filters = getFiltersForView(resolvedView);
    const searchQuery = getSearchForView(resolvedView);

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

    if (isSearchActive(searchQuery)) {
        url.searchParams.set("q", searchQuery.trim());
    }

    if (filters.idMin != null) {
        url.searchParams.set("id_min", String(filters.idMin));
    }
    if (filters.idMax != null) {
        url.searchParams.set("id_max", String(filters.idMax));
    }
    if (filters.balanceMin != null) {
        url.searchParams.set("balance_min", String(filters.balanceMin));
    }
    if (filters.balanceMax != null) {
        url.searchParams.set("balance_max", String(filters.balanceMax));
    }

    if (cursor) {
        url.searchParams.set("cursor", cursor);
    }
    return url.toString();
}

/** Append the next page of rows for infinite scroll.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @param {*} generation - Render generation token from beginOrdersRender.
 * @returns {Promise<void>}
 */
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

/** Render cached rows immediately for already-loaded view content.
 * @param {*} tableBody - Orders <tbody> element.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @param {*} colspan - Table column span for status rows.
 * @param {*} generation - Render generation token from beginOrdersRender.
 * @returns {Promise<void>}
 */
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

/**
 * Fetch first page from endpoint and render loading/success/error states.
 * @returns {Promise<void>}
 */
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
