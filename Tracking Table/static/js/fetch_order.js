/**
 * Get order information
 * Get order modal windows
 * @param {*} order_id 
 */
function get_order(order_id)
{
    /** Add loading indication */
    document.getElementById("hidden-row-" + order_id).appendChild(add_spinner(order_id));
    
    /** Get app specific resource address from element */
    let url_resource = document.getElementById(order_id).getAttribute("data-app-url");

    fetch(url_resource + order_id)
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

            /** Recompute height after dynamic content is fully updated */
            const hiddenRow = document.getElementById("hidden-row-" + order_id);
            onHiddenRowContentUpdated(hiddenRow);

        })
        .catch((error) => {

            /** Remove loading indication */
            remove_spinner(order_id);

            /** Show fallback message in placeholder */
            let hiddenTable = document.getElementById("hidden-table-" + order_id);
            if (hiddenTable)
            {
                hiddenTable.appendChild(create_order_error(order_id));
            }

            console.log(error);
        });
}

/**
 * Retry wrapper
 * Clear error messages
 * Adds spinner loading again before re-calling get_order
 *
 * @param {*} order_id 
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
    get_order(order_id);
}