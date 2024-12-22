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
            /** Load modal progress window */
            document.body.innerHTML += newHtml.getElementById("progress-window-" + order_id).innerHTML;
            /** Load modal delete window */
            document.body.innerHTML += newHtml.getElementById("delete-window-" + order_id).innerHTML;
            /** Load offcanvas history tab */
            document.body.innerHTML += newHtml.getElementById("offcanvas-history-tab-" + order_id).innerHTML;
            /** Load order table */
            document.getElementById("hidden-table-" + order_id)
                .innerHTML = newHtml.getElementsByClassName("order-view")[0].innerHTML;
            /** Add orders handlers */
            handle_orders_properties();
            handle_orders_history();
            handle_orders();
        })
        .catch((error) => {
            /** Remove spinner load */
            document.getElementById("order-spinner-" + order_id).remove();
            console.log("Error in getting order with ID: " + order_id);
            console.log(error);
        });
}