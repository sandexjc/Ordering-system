/*
 * dynamic/page.js
 * ---------------
 * Dynamic orders page orchestration: tab switch + DOMContentLoaded boot.
 *
 * Loaded last among dynamic/*.js from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on all other dynamic/*.js modules and base layout order scripts.
 */

/**
 * Keep the address bar on the view that is actually showing.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function rememberDynamicView(viewName) {
    const url = new URL(window.location.href);
    if (url.searchParams.get("view") === viewName) {
        return;
    }
    url.searchParams.set("view", viewName);
    window.history.replaceState(null, "", url);
}

/**
 * Show the active app in the tab title.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function updateDynamicTitle(viewName) {
    document.title = viewName === "vitrine" ? "TTable · Витрини" : "TTable · Разкрой";
}

/**
 * Switch between table/vitrine shells and trigger new async load.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function switchDynamicView(viewName) {
    const root = document.getElementById("dynamic-orders-root");
    const container = document.getElementById("dynamic-orders-table-container");
    if (!root || !container) {
        return;
    }

    const previousViewName = root.dataset.currentView;
    captureOpenRows(previousViewName);
    captureScrollPosition(previousViewName);
    captureLiveRowsHtml(previousViewName);
    teardownInfiniteScroll();

    const { generation } = beginOrdersRender(viewName);
    root.dataset.currentView = viewName;
    rememberDynamicView(viewName);
    updateDynamicTitle(viewName);
    updateDynamicNavigation(viewName);
    updateNewOrderLink(viewName);
    if (typeof syncSummarizeButtonVisibility === "function") {
        syncSummarizeButtonVisibility(viewName);
    }
    updateVisibleItemsCounter(0, viewName);
    ensureVitrineStylesIfNeeded(viewName);

    container.innerHTML = getShellMarkup(viewName);
    syncFilterControls(getFiltersForView(viewName), viewName);
    syncSearchControls(viewName);
    ensureFilterBounds(viewName).then((bounds) => {
        if (!bounds) {
            return;
        }
        syncFilterControls(getFiltersForView(viewName), viewName);
    });
    fetchAndRenderOrders({ viewName, generation }).then(() => {
        const rootNow = document.getElementById("dynamic-orders-root");
        if (!rootNow || rootNow.dataset.currentView !== viewName) {
            return;
        }
        if (generation !== ordersRenderGeneration) {
            return;
        }
        if (typeof focusOrdersLiveSync === "function") {
            focusOrdersLiveSync();
        }
    });
}

/** Initialize dynamic page behavior after DOM is ready. */
document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }

    ensureVitrineStylesIfNeeded(root.dataset.currentView);
    setupDynamicFilters();
    if (typeof setupDynamicSummarize === "function") {
        setupDynamicSummarize();
    }
    setupTableSortHeaders();
    setupDynamicSearch();
    syncSortHeaders(getFiltersForView(root.dataset.currentView || "table"));
    fetchAndRenderOrders({ viewName: root.dataset.currentView || "table" });
    if (typeof setupOrdersLiveSync === "function") {
        setupOrdersLiveSync();
    }

    const navButtons = document.querySelectorAll("[data-dynamic-view]");
    let touchViewAt = 0;

    function openDynamicViewFromControl(button, event) {
        const selectedView = button.dataset.dynamicView;
        const currentView = root.dataset.currentView;
        const plainLeftClick = !event
            || event.type !== "click"
            || (
                event.button === 0
                && !event.metaKey
                && !event.ctrlKey
                && !event.shiftKey
                && !event.altKey
            );
        if (button.tagName === "A" && !plainLeftClick) {
            return;
        }
        if (button.tagName === "A" && event) {
            event.preventDefault();
        }
        if (!selectedView || selectedView === currentView) {
            return;
        }
        switchDynamicView(selectedView);
    }

    navButtons.forEach((button) => {
        button.addEventListener("pointerup", (event) => {
            if (event.pointerType === "mouse") {
                return;
            }
            touchViewAt = Date.now();
            openDynamicViewFromControl(button, event);
        });
        button.addEventListener("click", (event) => {
            if (Date.now() - touchViewAt < 700) {
                if (button.tagName === "A") {
                    event.preventDefault();
                }
                return;
            }
            openDynamicViewFromControl(button, event);
        });
    });
});
