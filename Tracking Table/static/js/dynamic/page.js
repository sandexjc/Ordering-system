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
    teardownInfiniteScroll();

    const { generation } = beginOrdersRender(viewName);
    root.dataset.currentView = viewName;
    updateDynamicNavigation(viewName);
    updateNewOrderLink(viewName);
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
    setupTableSortHeaders();
    setupDynamicSearch();
    syncSortHeaders(getFiltersForView(root.dataset.currentView || "table"));
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
