/*
 * dynamic/render.js
 * -----------------
 * Row HTML builders, fade animations, shell/nav helpers, and post-render setup.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - dynamic/state.js
 * Runtime depends on:
 *   - dynamic/fetch.js → isOrdersRenderCurrent, getLiveOrdersBody
 *   - dynamic/cache.js → restoreCachedOrderDetails, restoreOpenRows
 *   - dynamic/search.js → highlightSearchInOrders
 *   - orders/row-expand/bind-rows.js → handle_orders
 *   - vitrine/js/virtual_rows.js → syncFrameHeights (optional)
 */

/**
 * Build loading-state row HTML while async request is in progress.
 * @param {*} colspan - Table column span for status rows.
 * @returns {string}
 */
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

/** Build error-state row HTML with retry action.
 * @param {*} colspan - Table column span for status rows.
 * @returns {string}
 */
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

/** Build empty-state row HTML when endpoint returns no rows.
 * @param {*} colspan - Table column span for status rows.
 * @returns {string}
 */
function buildEmptyRow(colspan) {
    return `
        <tr>
            <td colspan="${colspan}" class="text-center text-muted py-4">Няма поръчки за показване.</td>
        </tr>
    `;
}

/**
 * Footer status: loading more spinner.
 * @returns {string}
 */
function buildLoadingMoreStatus() {
    return `
        <div class="d-inline-flex align-items-center gap-2 text-muted">
            <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
            <span>Зареждане...</span>
        </div>
    `;
}

/**
 * Footer status: load-more error with retry.
 * @returns {string}
 */
function buildLoadMoreErrorStatus() {
    return `
        <div class="text-danger mb-2">Грешка при зареждане на още поръчки.</div>
        <button type="button" class="btn btn-sm btn-outline-primary" id="dynamic-orders-load-more-retry">Опитай отново</button>
    `;
}

/**
 * Footer status: end of list.
 * @returns {string}
 */
function buildEndOfListStatus() {
    return `<div class="text-muted">Това са всички поръчки</div>`;
}

/** Toggle active nav tab based on selected dynamic view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function updateDynamicNavigation(viewName) {
    const navButtons = document.querySelectorAll("[data-dynamic-view]");
    navButtons.forEach((button) => {
        const isActive = button.dataset.dynamicView === viewName;
        button.classList.toggle("active", isActive);
    });
}

/** Point "new order" button to table/vitrine create URL.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
function updateNewOrderLink(viewName) {
    const newOrderLink = document.getElementById("dynamic-new-order-link");
    if (!newOrderLink) {
        return;
    }

    const tableUrl = newOrderLink.dataset.tableUrl;
    const vitrineUrl = newOrderLink.dataset.vitrineUrl;
    newOrderLink.href = viewName === "vitrine" ? vitrineUrl : tableUrl;
}

/** Get pre-rendered shell markup template for selected view.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {string}
 */
function getShellMarkup(viewName) {
    const template = document.getElementById(`dynamic-${viewName}-shell-template`);
    if (!template) {
        return "";
    }
    return template.innerHTML;
}

/** Ensure a stylesheet is attached once in document head.
 * @param {*} id - Element id for the stylesheet link.
 * @param {*} href - Stylesheet URL.
 * @returns {void}
 */
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

/** Lazy-load vitrine CSS only when vitrine view is needed.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @returns {void}
 */
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

/** Fade out currently rendered rows before replacing tbody content.
 * @param {*} tableBody - Orders <tbody> element.
 * @returns {Promise<void>}
 */
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

/** Pick rows to animate. Prefer visible order rows so hidden detail rows are not staggered.
 * @param {*} rowsOrBody - Row elements array or tbody to animate.
 * @returns {void}
 */
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

/** Fade in rows with CSS transition-delay in one paint instead of per-row timers.
 * @param {*} rowsOrBody - Row elements array or tbody to animate.
 * @returns {void}
 */
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

/**
 * bindOrderRowHandlers
 * @returns {void}
 */
function bindOrderRowHandlers() {
    if (typeof handle_orders === "function") {
        handle_orders();
    }
}

/** Heavier post-render work that can wait until the fade has started.
 * @param {*} viewName - Dynamic view key ("table" | "vitrine").
 * @param {*} generation - Render generation token from beginOrdersRender.
 * @returns {void}
 */
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

/**
 * setupRenderedRows
 * @returns {void}
 */
function setupRenderedRows(viewName, generation, { deferHeavyWork = false } = {}) {
    if (!isOrdersRenderCurrent(generation, viewName)) {
        return;
    }
    bindOrderRowHandlers();
    highlightSearchInOrders(viewName);

    if (!deferHeavyWork) {
        finalizeRenderedRows(viewName, generation);
        return;
    }

    window.requestAnimationFrame(() => {
        window.setTimeout(() => finalizeRenderedRows(viewName, generation), 0);
    });
}

/**
 * setFooterStatus
 * @param {*} html - HTML string for the footer status area.
 * @returns {void}
 */
function setFooterStatus(html) {
    const statusNode = document.getElementById("dynamic-orders-status");
    if (!statusNode) {
        return;
    }
    statusNode.innerHTML = html || "";
}
