/*
 * dynamic/summarize.js
 * --------------------
 * Table-only summarize mode: fold/unfold card, toggle-select rows, totals table.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (load order):
 *   - dynamic/state.js → isSummarizeMode, summarizeSelectedIds
 * Runtime depends on:
 *   - orders/row-expand/open-close.js → closeHiddenRow, getLiveVisibleOrderRow
 *   - dynamic/fetch.js → getLiveOrdersBody
 *   - bootstrap Collapse
 *
 * Used by:
 *   - orders/row-expand/bind-rows.js → toggleSummarizeRowSelection
 *   - dynamic/render.js, dynamic/sync.js, dynamic/page.js
 */

/**
 * @returns {boolean}
 */
function isSummarizeFeatureEnabled() {
    const root = document.getElementById("dynamic-orders-root");
    return Boolean(root && root.dataset.summarizeEnabled === "1");
}

/**
 * @returns {HTMLElement|null}
 */
function getSummarizeCollapseEl() {
    return document.getElementById("dynamic-summarize-collapse");
}

/**
 * @returns {HTMLElement|null}
 */
function getFilterCollapseEl() {
    return document.getElementById("collapseExample");
}

/**
 * Hide a Bootstrap collapse without toggling if already closed.
 * @param {HTMLElement|null} el
 * @returns {void}
 */
function hideBootstrapCollapse(el) {
    if (!el || typeof bootstrap === "undefined" || !bootstrap.Collapse) {
        return;
    }
    bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).hide();
}

/**
 * Escape text for innerHTML line lists.
 * @param {string} value
 * @returns {string}
 */
function escapeSummarizeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[char]));
}

/**
 * Join unique lines as HTML breaks.
 * @param {string[]} lines
 * @returns {string}
 */
function summarizeHtmlLines(lines) {
    return lines.map(escapeSummarizeHtml).join("<br>");
}

/**
 * Parse "label - quantity" from a plate/edge cell. Uses the last " - ".
 * @param {string} text
 * @returns {{label: string, quantity: number}}
 */
function parseLabeledQuantity(text) {
    const trimmed = (text || "").trim();
    const separator = " - ";
    const index = trimmed.lastIndexOf(separator);
    if (index === -1) {
        return { label: trimmed, quantity: 0 };
    }
    const label = trimmed.slice(0, index).trim();
    const rawQty = trimmed.slice(index + separator.length).trim().replace(",", ".");
    const quantity = Number(rawQty);
    return {
        label,
        quantity: Number.isFinite(quantity) ? quantity : 0,
    };
}

/**
 * Format a summed quantity without trailing zeros when whole.
 * @param {number} value
 * @returns {string}
 */
function formatSummarizeQuantity(value) {
    if (!Number.isFinite(value)) {
        return "0";
    }
    const rounded = Math.round(value * 10) / 10;
    if (Number.isInteger(rounded)) {
        return String(rounded);
    }
    return rounded.toFixed(1);
}

/**
 * @param {number} value
 * @returns {string}
 */
function formatSummarizeBalance(value) {
    if (!Number.isFinite(value)) {
        return "0.00";
    }
    return value.toFixed(2);
}

/**
 * Sorted "label — qty unit" lines from a Map.
 * @param {Map<string, number>} grouped
 * @param {string} [unit]
 * @returns {string[]}
 */
function groupedQuantityLines(grouped, unit) {
    return Array.from(grouped.entries())
        .sort((left, right) => left[0].localeCompare(right[0], "bg"))
        .map(([label, quantity]) => {
            const qty = formatSummarizeQuantity(quantity);
            return unit ? `${label} — ${qty} ${unit}` : `${label} — ${qty}`;
        });
}

/**
 * Client name is the first line of the client cell (before telephone).
 * @param {HTMLElement} row
 * @returns {string}
 */
function getOrderClientName(row) {
    const clientCell = row.children[2];
    if (!clientCell) {
        return "";
    }
    let name = "";
    for (const node of clientCell.childNodes) {
        if (node.nodeName === "BR") {
            break;
        }
        name += node.textContent || "";
    }
    return name.trim();
}

/**
 * Close every expanded order detail row on the live table.
 * @returns {void}
 */
function closeAllOpenOrderRows() {
    document.querySelectorAll(".hiddenRows").forEach((hiddenRow) => {
        const isOpen = hiddenRow._isOpen
            || hiddenRow.classList.contains("is-open")
            || hiddenRow.classList.contains("orderClicked");
        if (!isOpen || typeof closeHiddenRow !== "function") {
            return;
        }
        const rowId = hiddenRow.id.replace("hidden-row-", "");
        const visibleRow = typeof getLiveVisibleOrderRow === "function"
            ? getLiveVisibleOrderRow(rowId)
            : document.querySelector('tr.visibleRows[data-row="' + rowId + '"]');
        closeHiddenRow(hiddenRow, visibleRow);
    });
}

/**
 * Selected live rows in a stable order (numeric id).
 * @returns {HTMLElement[]}
 */
function getSelectedSummarizeRows() {
    const rows = [];
    summarizeSelectedIds.forEach((orderId) => {
        const row = document.querySelector('tr.visibleRows[data-row="' + orderId + '"]');
        if (row) {
            rows.push(row);
        }
    });
    rows.sort((left, right) => {
        const leftId = Number(left.getAttribute("data-row") || left.id);
        const rightId = Number(right.getAttribute("data-row") || right.id);
        return leftId - rightId;
    });
    return rows;
}

/**
 * Reset both summarize tables to empty-selection values.
 * @returns {void}
 */
function resetSummarizeTable() {
    const setText = (id, value) => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
        }
    };
    setText("summarize-count", "0 бр");
    setText("summarize-clients-count", "0 бр");
    setText("summarize-plates-total", "0 бр");
    setText("summarize-edges-total", "0 лм");
    setText("summarize-weight-total", "");
    setText("summarize-balance", "0.00 €");
    setText("summarize-order-ids", "");
    setText("summarize-clients", "");
    setText("summarize-plates", "");
    setText("summarize-edges", "");
    setText("summarize-weights", "");
    setText("summarize-balances", "");
    hideBootstrapCollapse(document.getElementById("dynamic-summarize-groups"));
}

/**
 * @param {Map<string, number>} grouped
 * @param {string} [unit]
 * @returns {string}
 */
function buildGroupedLinesHtml(grouped, unit) {
    if (!grouped.size) {
        return "";
    }
    return summarizeHtmlLines(groupedQuantityLines(grouped, unit));
}

/**
 * Recompute both summarize tables from currently selected live rows.
 * @returns {void}
 */
function refreshSummarizeTotals() {
    const countEl = document.getElementById("summarize-count");
    const clientsCountEl = document.getElementById("summarize-clients-count");
    const platesTotalEl = document.getElementById("summarize-plates-total");
    const edgesTotalEl = document.getElementById("summarize-edges-total");
    const balanceEl = document.getElementById("summarize-balance");
    const orderIdsEl = document.getElementById("summarize-order-ids");
    const clientsEl = document.getElementById("summarize-clients");
    const platesEl = document.getElementById("summarize-plates");
    const edgesEl = document.getElementById("summarize-edges");
    const balancesEl = document.getElementById("summarize-balances");
    if (!countEl || !clientsCountEl || !platesTotalEl || !edgesTotalEl || !balanceEl
        || !orderIdsEl || !clientsEl || !platesEl || !edgesEl || !balancesEl) {
        return;
    }

    const selectedRows = getSelectedSummarizeRows();
    const orderIds = [];
    const balances = [];
    const clients = new Set();
    const plates = new Map();
    const edges = new Map();
    let platesTotal = 0;
    let edgesTotal = 0;
    let balanceTotal = 0;

    selectedRows.forEach((row) => {
        const orderId = String(row.getAttribute("data-row") || row.id || "");
        if (orderId) {
            orderIds.push(orderId);
        }

        const clientName = getOrderClientName(row);
        if (clientName) {
            clients.add(clientName);
        }

        row.querySelectorAll(".Plate").forEach((el) => {
            const parsed = parseLabeledQuantity(el.textContent);
            if (!parsed.label) {
                return;
            }
            platesTotal += parsed.quantity;
            plates.set(parsed.label, (plates.get(parsed.label) || 0) + parsed.quantity);
        });

        row.querySelectorAll(".Edge").forEach((el) => {
            const parsed = parseLabeledQuantity(el.textContent);
            if (!parsed.label) {
                return;
            }
            edgesTotal += parsed.quantity;
            edges.set(parsed.label, (edges.get(parsed.label) || 0) + parsed.quantity);
        });

        const balance = Number(row.getAttribute("data-sort-balance"));
        const safeBalance = Number.isFinite(balance) ? balance : 0;
        balances.push(`${formatSummarizeBalance(safeBalance)} €`);
        balanceTotal += safeBalance;
    });

    countEl.textContent = `${selectedRows.length} бр`;
    clientsCountEl.textContent = `${clients.size} бр`;
    platesTotalEl.textContent = `${formatSummarizeQuantity(platesTotal)} бр`;
    edgesTotalEl.textContent = `${formatSummarizeQuantity(edgesTotal)} лм`;
    balanceEl.textContent = `${formatSummarizeBalance(balanceTotal)} €`;

    orderIdsEl.innerHTML = summarizeHtmlLines(orderIds);
    clientsEl.innerHTML = summarizeHtmlLines(Array.from(clients).sort((left, right) => (
        left.localeCompare(right, "bg")
    )));
    platesEl.innerHTML = buildGroupedLinesHtml(plates, "бр");
    edgesEl.innerHTML = buildGroupedLinesHtml(edges, "лм");
    balancesEl.innerHTML = summarizeHtmlLines(balances);
}

/**
 * Toggle one order row in summarize selection.
 * @param {HTMLElement} visibleRow
 * @returns {void}
 */
function toggleSummarizeRowSelection(visibleRow) {
    if (!visibleRow) {
        return;
    }
    const orderId = String(visibleRow.getAttribute("data-row") || visibleRow.id || "");
    if (!orderId) {
        return;
    }
    if (summarizeSelectedIds.has(orderId)) {
        summarizeSelectedIds.delete(orderId);
        visibleRow.classList.remove("summarize-selected");
    } else {
        summarizeSelectedIds.add(orderId);
        visibleRow.classList.add("summarize-selected");
    }
    refreshSummarizeTotals();
}

/**
 * Re-apply selection classes after render/sync; drop ids no longer in the DOM.
 * @returns {void}
 */
function restoreSummarizeSelection() {
    if (!isSummarizeMode) {
        return;
    }
    const liveIds = new Set();
    document.querySelectorAll("tr.visibleRows").forEach((row) => {
        const orderId = String(row.getAttribute("data-row") || row.id || "");
        if (!orderId || !summarizeSelectedIds.has(orderId)) {
            return;
        }
        row.classList.add("summarize-selected");
        liveIds.add(orderId);
    });
    Array.from(summarizeSelectedIds).forEach((orderId) => {
        if (!liveIds.has(orderId)) {
            summarizeSelectedIds.delete(orderId);
        }
    });
    refreshSummarizeTotals();
}

/**
 * Enter selection mode: close filter/details and mark the root.
 * @returns {void}
 */
function enterSummarizeMode() {
    if (isSummarizeMode) {
        return;
    }
    hideBootstrapCollapse(getFilterCollapseEl());
    closeAllOpenOrderRows();
    isSummarizeMode = true;
    const root = document.getElementById("dynamic-orders-root");
    if (root) {
        root.classList.add("summarize-mode");
    }
    restoreSummarizeSelection();
    refreshSummarizeModeSummary();
}

/**
 * Leave selection mode: restore expand-on-click and clear selection.
 * @returns {void}
 */
function exitSummarizeMode() {
    isSummarizeMode = false;
    summarizeSelectedIds.clear();
    document.querySelectorAll("tr.visibleRows.summarize-selected").forEach((row) => {
        row.classList.remove("summarize-selected");
    });
    const root = document.getElementById("dynamic-orders-root");
    if (root) {
        root.classList.remove("summarize-mode");
    }
    resetSummarizeTable();
    refreshSummarizeModeSummary();
}

/**
 * Refresh the red status line under the items counter.
 * @returns {void}
 */
function refreshSummarizeModeSummary() {
    if (typeof updateVisibleFiltersSummary !== "function") {
        return;
    }
    const root = document.getElementById("dynamic-orders-root");
    const viewName = root?.dataset.currentView || "table";
    const filters = typeof getFiltersForView === "function"
        ? getFiltersForView(viewName)
        : null;
    updateVisibleFiltersSummary(filters, viewName);
}

/**
 * Show the summarize button only on the table view.
 * @param {string} viewName
 * @returns {void}
 */
function syncSummarizeButtonVisibility(viewName) {
    const toggle = document.getElementById("dynamic-summarize-toggle");
    if (!toggle) {
        return;
    }
    const show = viewName === "table" && isSummarizeFeatureEnabled();
    toggle.classList.toggle("d-none", !show);
    if (!show) {
        hideBootstrapCollapse(getSummarizeCollapseEl());
    }
}

/**
 * Wire collapse mutual-exclusion and enter/exit handlers.
 * @returns {void}
 */
function setupDynamicSummarize() {
    if (!isSummarizeFeatureEnabled()) {
        return;
    }
    const summarizeRoot = getSummarizeCollapseEl();
    if (!summarizeRoot || summarizeRoot.dataset.summarizeBound === "1") {
        return;
    }
    summarizeRoot.dataset.summarizeBound = "1";

    summarizeRoot.addEventListener("show.bs.collapse", (event) => {
        if (event.target !== summarizeRoot) {
            return;
        }
        hideBootstrapCollapse(getFilterCollapseEl());
        enterSummarizeMode();
    });
    summarizeRoot.addEventListener("hide.bs.collapse", (event) => {
        if (event.target !== summarizeRoot) {
            return;
        }
        exitSummarizeMode();
    });

    const filterRoot = getFilterCollapseEl();
    if (filterRoot) {
        filterRoot.addEventListener("show.bs.collapse", () => {
            hideBootstrapCollapse(summarizeRoot);
        });
    }

    const root = document.getElementById("dynamic-orders-root");
    syncSummarizeButtonVisibility(root?.dataset.currentView || "table");
}
