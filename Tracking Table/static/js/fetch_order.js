/**
 * Get order information
 * Get order modal windows
 * Add HTML elements
 * Reload all orders content and callbacks
 * @param {*} order_id 
 */

function get_order(order_id)
{
    fetch('/table/viewOrder/' + order_id)
        .then((response) => {
            return response.text()
        })
        .then((html) => {

            /** Remove spinner load */
            document.getElementById("order-spinner-" + order_id).remove();
            let parser = new DOMParser();
            let newHtml = parser.parseFromString(html, 'text/html');

            /** Offers does not have progress tracking */
            let progressWindow = newHtml.getElementById("progress-window-" + order_id);
            if (progressWindow) {
                document.body.innerHTML += progressWindow.innerHTML;
            }

            /** Load modal delete window */
            document.body.innerHTML += newHtml.getElementById("delete-window-" + order_id).innerHTML;

            /** Load offcanvas history tab */
            document.body.innerHTML += newHtml.getElementById("offcanvas-history-tab-" + order_id).innerHTML;

            /** Load order table */
            document.getElementById("hidden-table-" + order_id)
                .innerHTML = newHtml.getElementsByClassName("order-view")[0].innerHTML;

            /** Add back orders handlers */
            handle_orders_properties();
            handle_orders_history();
            handle_orders();
        })
        .catch((error) => {
            /** Remove spinner load */
            document.getElementById("order-spinner-" + order_id).remove();

            /** Show fallback message in placeholder */
            let hiddenTable = document.getElementById("hidden-table-" + order_id);
            if (hiddenTable) {
                hiddenTable.innerHTML = `
                    <div style="text-align: center; padding: 10px;">
                        <h6 style="color: red;">⚠️ Could not load order details...</h6>
                        <button class="btn btn-sm btn-outline-primary" onclick="retry_order(${order_id})">
                            🔄 Retry
                        </button>
                    </div>
                `;
            }

            console.log(error);
        });
}

/**
 * Retry wrapper
 * Clear error messages
 * Adds spinner again before re-calling get_order
 *
 * @param {*} order_id 
 */
function retry_order(order_id) {
    let hiddenTable = document.getElementById("hidden-table-" + order_id);
    if (hiddenTable) {
        hiddenTable.innerHTML = "";
        hiddenTable.appendChild(spinner(order_id));
    }
    get_order(order_id);
}