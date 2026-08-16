/*
 * orders/details/fetch.js
 * -----------------------
 * Fetch and inject expanded order / vitrine detail HTML (progress, delete, history, view).
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on (runtime):
 *   - orders/details/spinner.js
 *   - orders/details/error.js
 *   - orders/row-expand/transitions.js → onHiddenRowContentUpdated
 *   - orders/actions/properties.js    → handle_orders_properties
 *   - orders/actions/history.js       → handle_orders_history
 *
 * Used by:
 *   - orders/row-expand/open-close.js → openHiddenRow
 *   - common/.../order_toolbar.html refresh button (retry_order)
 *   - orders/details/error.js retry button
 */

/**
 * Resolve the current dynamic view name (table / vitrine) when on the dynamic page.
 *
 * @returns {string|null} View name from `#dynamic-orders-root`, or null outside that page.
 */
function get_current_dynamic_view_name()
{
    let root = document.getElementById("dynamic-orders-root");
    if (!root) {
        return null;
    }
    return root.getAttribute("data-current-view");
}

/**
 * Store `#hidden-table-{id}` HTML into the per-view dynamic cache to avoid refetch.
 *
 * @param {string|number} order_id - Order / vitrine id whose details to cache.
 * @returns {void}
 */
function cache_order_details(order_id)
{
    if (!window.viewOrdersCache) {
        return;
    }

    let current_view = get_current_dynamic_view_name();
    if (!current_view) {
        return;
    }

    let cache_entry = window.viewOrdersCache.get(current_view);
    if (!cache_entry) {
        return;
    }

    let hidden_table = document.getElementById("hidden-table-" + order_id);
    if (!hidden_table) {
        return;
    }

    if (!cache_entry.orderDetails) {
        cache_entry.orderDetails = {};
    }
    cache_entry.orderDetails[order_id] = hidden_table.innerHTML;
    window.viewOrdersCache.set(current_view, cache_entry);
}

/**
 * Fetch order/vitrine detail HTML and inject progress modal, delete modal,
 * history offcanvas, and the in-row order view. Shows spinner while loading;
 * on failure shows create_order_error UI.
 *
 * @param {string|number} order_id - Order / vitrine id (element id + fetch URL suffix).
 * @returns {void}
 */
function get_order(order_id)
{
    const orderKey = String(order_id);
    const inFlight = window.ordersDetailsInFlight;
    if (inFlight) {
        if (inFlight.has(orderKey)) {
            return;
        }
        inFlight.add(orderKey);
    }

    const hiddenRow = document.getElementById("hidden-row-" + order_id);
    const hiddenTable = document.getElementById("hidden-table-" + order_id);
    const rowEl = document.getElementById(order_id);
    if (!rowEl) {
        if (inFlight) {
            inFlight.delete(orderKey);
        }
        return;
    }

    /** Hide fold button while loading; spinner lives inside the content area. */
    set_hidden_row_close_visible(order_id, false);
    if (hiddenTable) {
        const previousView = document.getElementById("order-view-" + order_id);
        if (previousView) {
            previousView.remove();
        }
        const previousError = document.getElementById("order-error-" + order_id);
        if (previousError) {
            previousError.remove();
        }
        hiddenTable.appendChild(add_spinner(order_id));
    }
    if (typeof onHiddenRowContentUpdated === "function") {
        onHiddenRowContentUpdated(hiddenRow);
    }

    let url_resource = rowEl.getAttribute("data-app-url");
    let url = url_resource + order_id;
    // Dynamic page only: ViewOrder / ViewVitrine skip the progress modal.
    if (get_current_dynamic_view_name()) {
        url += (url.indexOf("?") === -1 ? "?" : "&") + "dynamic=1";
    }

    fetch(url)
        .then((response) => {
            /** Raise an error for a non network issues as well */
            if (!response.ok) {
                throw new Error("HTTP " + response.status + " " + response.statusText);
            }
            return response.text()
        })
        .then((html) => {
            /** Parse new html */
            let parser = new DOMParser();
            let newHtml = parser.parseFromString(html, 'text/html');

            /** Remove loading indication */
            remove_spinner(order_id);

            /*
             * Load progress tracking form
             * Offers does not have progress tracking, only orders does
             */
            let new_progress_form = newHtml.getElementById("progress-window-" + order_id);
            let prev_progress_form = document.getElementById("progress-window-" + order_id);
            if (new_progress_form) {
                if (prev_progress_form)
                {
                    /** Replace previous progress window if any */
                    prev_progress_form.replaceWith(new_progress_form.cloneNode(true));
                }
                else
                {
                    /** Load new progress window for specific order */
                    document.body.appendChild(new_progress_form.cloneNode(true));
                }
            }

            /*
             * Load modal delete window
             */
            let modal_delete_form = document.getElementById("delete-window-" + order_id);
            let new_modal_delete = newHtml.getElementById("delete-window-" + order_id);
            if (!modal_delete_form && new_modal_delete)
            {
                document.body.appendChild(new_modal_delete.cloneNode(true));
            }

            /*
             * Load offcanvas history tab
             */
            let history_tab = document.getElementById("offcanvas-history-tab-" + order_id);
            let new_history_tab = newHtml.getElementById("offcanvas-history-tab-" + order_id);
            if (!history_tab && new_history_tab)
            {
                document.body.appendChild(new_history_tab.cloneNode(true));
            }

            /*
             * Load order progress view table
             */
            let order_progress_view = document.getElementById("order-view-" + order_id);
            let new_progress_view = newHtml.getElementById("order-view-" + order_id);
            if (new_progress_view)
            {
                if (order_progress_view)
                {
                    order_progress_view.replaceWith(new_progress_view.cloneNode(true));
                }
                else
                {
                    document.getElementById("hidden-table-" + order_id).appendChild(new_progress_view.cloneNode(true));
                }
            }

            handle_orders_properties();
            handle_orders_history();

            /** Show fold button only after content is ready */
            set_hidden_row_close_visible(order_id, true);

            /** Recompute height after dynamic content is fully updated */
            onHiddenRowContentUpdated(document.getElementById("hidden-row-" + order_id));
            cache_order_details(order_id);

        })
        .catch((error) => {

            /** Remove loading indication */
            remove_spinner(order_id);

            /** Show fallback message in placeholder */
            let errorHiddenTable = document.getElementById("hidden-table-" + order_id);
            if (errorHiddenTable)
            {
                errorHiddenTable.appendChild(create_order_error(order_id));
            }

            set_hidden_row_close_visible(order_id, true);
            onHiddenRowContentUpdated(document.getElementById("hidden-row-" + order_id));

            console.log(error);
        })
        .finally(() => {
            if (inFlight) {
                inFlight.delete(orderKey);
            }
        });
}

/**
 * Clear error/order-view fragments and re-fetch order details.
 *
 * @param {string|number} order_id - Order / vitrine id to reload.
 * @returns {void}
 */
function retry_order(order_id) {
    let hiddenTable = document.getElementById("hidden-table-" + order_id);
    if (hiddenTable) {

        /** Remove error view if any */
        let error_view = document.getElementById("order-error-" + order_id);
        if (error_view)
        {
            document.getElementById("order-error-" + order_id).remove();
        }

        /** Remove previos order table */
        let order_view = document.getElementById("order-view-" + order_id);
        if (order_view)
        {
            document.getElementById("order-view-" + order_id).remove();
        }

    }
    set_hidden_row_close_visible(order_id, false);
    get_order(order_id);
}
