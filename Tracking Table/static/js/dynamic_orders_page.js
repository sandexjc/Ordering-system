/** Update top counter text to match currently rendered rows. */
function updateVisibleItemsCounter(visibleItems) {
    const itemsNode = document.getElementById("visible-items-count");
    const suffixNode = document.getElementById("visible-items-suffix");

    if (itemsNode) {
        itemsNode.textContent = visibleItems;
    }
    if (suffixNode) {
        suffixNode.textContent = visibleItems === 1 ? "" : "a";
    }
}

/** Cache rows per view to avoid re-fetching on tab switch. */
const viewOrdersCache = window.viewOrdersCache || new Map();
window.viewOrdersCache = viewOrdersCache;

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
    const rows = Array.from(tableBody.querySelectorAll("tr"));
    if (!rows.length) {
        return;
    }

    await Promise.all(
        rows.map(
            (row) =>
                new Promise((resolve) => {
                    row.style.transition = "opacity 100ms ease-out";
                    row.style.opacity = "0";
                    window.setTimeout(resolve, 110);
                })
        )
    );
}

/** Fade in newly rendered rows with a tiny stagger for smoother reveal. */
function fadeInRows(tableBody) {
    const rows = Array.from(tableBody.querySelectorAll("tr"));
    rows.forEach((row, index) => {
        row.style.opacity = "0";
        row.style.transform = "translateY(4px)";
        row.style.transition = "opacity 180ms ease-in, transform 180ms ease-in";
        row.style.willChange = "opacity, transform";

        window.setTimeout(() => {
            row.style.opacity = "1";
            row.style.transform = "translateY(0)";
        }, index * 12);

        row.addEventListener(
            "transitionend",
            () => {
                row.style.transition = "";
                row.style.transform = "";
                row.style.willChange = "";
            },
            { once: true }
        );
    });
}

/** Run post-render setup hooks for row interactions and vitrine layout. */
function setupRenderedRows() {
    if (typeof handle_orders === "function") {
        handle_orders();
    }
    if (typeof syncFrameHeights === "function") {
        syncFrameHeights();
    }
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

/** Capture currently expanded row ids for a specific view before switching away. */
function captureOpenRows(viewName) {
    if (!viewName) {
        return;
    }
    const cacheEntry = viewOrdersCache.get(viewName);
    if (!cacheEntry) {
        return;
    }

    const openRowIds = Array.from(document.querySelectorAll(".hiddenRows.is-open"))
        .map((hiddenRow) => hiddenRow.id.replace("hidden-row-", ""))
        .filter(Boolean);

    cacheEntry.openRowIds = openRowIds;
    viewOrdersCache.set(viewName, cacheEntry);
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
        if (hiddenRow.classList.contains("is-open")) {
            return;
        }
        visibleRow.click();
    });
}

/** Render cached rows immediately for already-loaded view content. */
async function renderCachedRowsIfAvailable(tableBody, viewName, colspan) {
    const cached = viewOrdersCache.get(viewName);
    if (!cached) {
        return false;
    }

    await fadeOutRows(tableBody);
    tableBody.innerHTML = cached.rowsHtml || buildEmptyRow(colspan);
    fadeInRows(tableBody);
    updateVisibleItemsCounter(cached.visibleItems);
    setupRenderedRows();
    restoreCachedOrderDetails(viewName);
    restoreOpenRows(viewName);
    return true;
}

/** Fetch rows from endpoint and render loading/success/error states. */
async function fetchAndRenderOrders(forceRefresh = false) {
    const tableBody = document.getElementById("dynamic-orders-body");
    if (!tableBody) {
        return;
    }

    const endpoint = tableBody.dataset.endpoint;
    const colspan = Number.parseInt(tableBody.dataset.colspan || "10", 10);
    const viewName = tableBody.dataset.view || "table";
    if (!endpoint) {
        return;
    }

    if (!forceRefresh) {
        const renderedFromCache = await renderCachedRowsIfAvailable(tableBody, viewName, colspan);
        if (renderedFromCache) {
            return;
        }
    }

    await fadeOutRows(tableBody);
    tableBody.innerHTML = buildLoadingRow(colspan);

    try {
        const response = await fetch(endpoint, {
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
        const previousCache = viewOrdersCache.get(viewName);
        viewOrdersCache.set(viewName, {
            rowsHtml,
            visibleItems,
            orderDetails: previousCache?.orderDetails || {},
        });

        tableBody.innerHTML = rowsHtml || buildEmptyRow(colspan);
        fadeInRows(tableBody);
        updateVisibleItemsCounter(visibleItems);
        setupRenderedRows();
    } catch (error) {
        console.error(error);
        tableBody.innerHTML = buildErrorRow(colspan);
        fadeInRows(tableBody);
        updateVisibleItemsCounter(0);

        const retryButton = document.getElementById("dynamic-orders-retry");
        if (retryButton) {
            retryButton.addEventListener("click", () => fetchAndRenderOrders(true), { once: true });
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

    root.dataset.currentView = viewName;
    updateDynamicNavigation(viewName);
    updateNewOrderLink(viewName);
    updateVisibleItemsCounter(0);
    ensureVitrineStylesIfNeeded(viewName);

    container.innerHTML = getShellMarkup(viewName);
    fetchAndRenderOrders();
}

/** Initialize dynamic page behavior after DOM is ready. */
document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return;
    }

    ensureVitrineStylesIfNeeded(root.dataset.currentView);
    fetchAndRenderOrders();

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
