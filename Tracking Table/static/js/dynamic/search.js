/*
 * dynamic/search.js
 * -----------------
 * Expandable search UI, debounce, and yellow highlight marks.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - dynamic/state.js
 *   - dynamic/filters.js → getFiltersForView, updateVisibleFiltersSummary, updateVisibleItemsCounter
 * Runtime depends on:
 *   - dynamic/cache.js / fetch.js → updateViewCache, beginOrdersRender, fetchAndRenderOrders, getLiveOrdersBody
 */

/**
 * Active search query for a view (empty when inactive).
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {string}
 */
function getSearchForView(viewName) {
    const cacheEntry = viewOrdersCache.get(viewName);
    if (cacheEntry && typeof cacheEntry.searchQuery === "string") {
        return cacheEntry.searchQuery;
    }
    return "";
}

/** True when search text is long enough to be sent to the backend.
 * @param {*} searchQuery - Committed search string (or empty).
 * @returns {boolean}
 */
function isSearchActive(searchQuery) {
    return (searchQuery || "").trim().length >= SEARCH_MIN_LENGTH;
}

/** Normalize a raw input value into the committed search query (or empty).
 * @param {*} value - Input value to parse or escape.
 * @returns {string}
 */
function normalizeSearchQuery(value) {
    const trimmed = (value || "").trim();
    return trimmed.length >= SEARCH_MIN_LENGTH ? trimmed : "";
}

/** Toggle search badge and keep the field open while a query is active.
 * @param {*} searchQuery - Committed search string (or empty).
 * @returns {void}
 */
function updateSearchBadge(searchQuery) {
    const active = isSearchActive(searchQuery);
    const badge = document.getElementById("dynamic-search-badge");
    if (badge) {
        badge.classList.toggle("d-none", !active);
    }

    const searchRoot = document.getElementById("dynamic-search");
    const toggle = document.getElementById("dynamic-search-toggle");
    if (active && searchRoot) {
        searchRoot.classList.add("is-open");
        if (toggle) {
            toggle.setAttribute("aria-expanded", "true");
        }
    }
}

/** Sync the search input to the active view's stored query.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function syncSearchControls(viewName) {
    const searchQuery = getSearchForView(viewName);
    const input = document.getElementById("dynamic-search-input");
    if (input && document.activeElement !== input) {
        input.value = searchQuery;
    }
    updateSearchBadge(searchQuery);
}

/**
 * Open the expandable search field and focus the input.
 * @returns {void}
 */
function openDynamicSearch({ focusInput = true } = {}) {
    const searchRoot = document.getElementById("dynamic-search");
    const toggle = document.getElementById("dynamic-search-toggle");
    const input = document.getElementById("dynamic-search-input");
    if (!searchRoot) {
        return;
    }

    searchRoot.classList.add("is-open");
    if (toggle) {
        toggle.setAttribute("aria-expanded", "true");
    }
    if (focusInput && input) {
        window.requestAnimationFrame(() => input.focus());
    }
}

/**
 * Close the search field unless it is focused or has an active query.
 * @returns {void}
 */
function maybeCloseDynamicSearch() {
    const searchRoot = document.getElementById("dynamic-search");
    const toggle = document.getElementById("dynamic-search-toggle");
    const input = document.getElementById("dynamic-search-input");
    if (!searchRoot) {
        return;
    }

    const root = document.getElementById("dynamic-orders-root");
    const viewName = root?.dataset.currentView || "table";
    if (isSearchActive(getSearchForView(viewName))) {
        return;
    }
    if (input && document.activeElement === input) {
        return;
    }
    if (searchRoot.matches(":hover")) {
        return;
    }

    searchRoot.classList.remove("is-open");
    if (toggle) {
        toggle.setAttribute("aria-expanded", "false");
    }
}

/** Persist search query, clear cached rows, and refetch.
 * @param {*} rawValue - Raw search input value.
 * @returns {void}
 */
function applySearchAndRefresh(rawValue) {
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }

    const viewName = root.dataset.currentView || "table";
    const searchQuery = normalizeSearchQuery(rawValue);
    if (getSearchForView(viewName) === searchQuery) {
        syncSearchControls(viewName);
        updateVisibleFiltersSummary(getFiltersForView(viewName), viewName);
        return;
    }

    updateViewCache(viewName, {
        searchQuery,
        rowsHtml: "",
        visibleItems: 0,
        nextCursor: null,
        hasMore: false,
        openRowIds: [],
        orderDetails: {},
        scrollY: 0,
    });
    syncSearchControls(viewName);
    updateVisibleItemsCounter(0, viewName);

    const { generation } = beginOrdersRender(viewName);
    fetchAndRenderOrders({ forceRefresh: true, viewName, generation });
}

/** Schedule a debounced search commit after typing pauses.
 * @param {*} rawValue - Raw search input value.
 * @returns {void}
 */
function scheduleSearchCommit(rawValue) {
    if (searchDebounceTimer) {
        window.clearTimeout(searchDebounceTimer);
    }
    searchDebounceTimer = window.setTimeout(() => {
        searchDebounceTimer = null;
        applySearchAndRefresh(rawValue);
    }, SEARCH_DEBOUNCE_MS);
}

/**
 * Wire expandable search UI + debounced requests.
 * @returns {void}
 */
function setupDynamicSearch() {
    const searchRoot = document.getElementById("dynamic-search");
    const toggle = document.getElementById("dynamic-search-toggle");
    const input = document.getElementById("dynamic-search-input");
    if (!searchRoot || !toggle || !input || searchRoot.dataset.searchBound === "1") {
        return;
    }
    searchRoot.dataset.searchBound = "1";

    const root = document.getElementById("dynamic-orders-root");
    const initialView = root?.dataset.currentView || "table";
    syncSearchControls(initialView);

    searchRoot.addEventListener("mouseenter", () => {
        openDynamicSearch({ focusInput: false });
    });
    searchRoot.addEventListener("mouseleave", () => {
        maybeCloseDynamicSearch();
    });

    toggle.addEventListener("click", (event) => {
        event.preventDefault();
        if (searchRoot.classList.contains("is-open") && document.activeElement === input) {
            input.blur();
            maybeCloseDynamicSearch();
            return;
        }
        openDynamicSearch({ focusInput: true });
    });

    input.addEventListener("focus", () => {
        openDynamicSearch({ focusInput: false });
    });
    input.addEventListener("blur", () => {
        window.setTimeout(() => maybeCloseDynamicSearch(), 120);
    });
    input.addEventListener("input", () => {
        openDynamicSearch({ focusInput: false });
        scheduleSearchCommit(input.value);
    });
    input.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            input.blur();
            maybeCloseDynamicSearch();
        }
    });
}

/**
 * escapeRegExp
 * @param {*} value - Input value to parse or escape.
 * @returns {void}
 */
function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Remove previous search highlight marks from a container.
 * @param {*} container - DOM container to scan/update.
 * @returns {void}
 */
function clearSearchHighlights(container) {
    if (!container) {
        return;
    }
    container.querySelectorAll("mark.search-highlight").forEach((mark) => {
        const parent = mark.parentNode;
        if (!parent) {
            return;
        }
        parent.replaceChild(document.createTextNode(mark.textContent || ""), mark);
        parent.normalize();
    });
}

/** Wrap case-insensitive matches of the active search term in yellow marks.
 * @param {*} container - DOM container to scan/update.
 * @param {*} searchQuery - Committed search string (or empty).
 * @returns {void}
 */
function highlightSearchMatches(container, searchQuery) {
    if (!container) {
        return;
    }

    clearSearchHighlights(container);
    if (!isSearchActive(searchQuery)) {
        return;
    }

    const term = searchQuery.trim();
    const regex = new RegExp(`(${escapeRegExp(term)})`, "gi");
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
            if (!node.nodeValue || !node.nodeValue.trim()) {
                return NodeFilter.FILTER_REJECT;
            }
            const parent = node.parentElement;
            if (!parent) {
                return NodeFilter.FILTER_REJECT;
            }
            if (parent.closest("script, style, mark.search-highlight")) {
                return NodeFilter.FILTER_REJECT;
            }
            if (!parent.closest("tr.visibleRows")) {
                return NodeFilter.FILTER_REJECT;
            }
            return NodeFilter.FILTER_ACCEPT;
        },
    });

    const textNodes = [];
    while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
    }

    textNodes.forEach((textNode) => {
        const text = textNode.nodeValue;
        regex.lastIndex = 0;
        if (!regex.test(text)) {
            return;
        }
        regex.lastIndex = 0;

        const fragment = document.createDocumentFragment();
        let lastIndex = 0;
        let match = regex.exec(text);
        while (match) {
            if (match.index > lastIndex) {
                fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
            }
            const mark = document.createElement("mark");
            mark.className = "search-highlight";
            mark.textContent = match[0];
            fragment.appendChild(mark);
            lastIndex = match.index + match[0].length;
            if (match[0].length === 0) {
                regex.lastIndex += 1;
            }
            match = regex.exec(text);
        }
        if (lastIndex < text.length) {
            fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
        }
        textNode.parentNode.replaceChild(fragment, textNode);
    });
}

/** Highlight active search matches in the live orders table body.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function highlightSearchInOrders(viewName) {
    const tableBody = getLiveOrdersBody(viewName);
    if (!tableBody) {
        return;
    }
    highlightSearchMatches(tableBody, getSearchForView(viewName));
}
