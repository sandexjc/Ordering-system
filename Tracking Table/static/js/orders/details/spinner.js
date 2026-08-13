/*
 * orders/details/spinner.js
 * -------------------------
 * Loading spinner and fold-button visibility for expanded order details.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Used by:
 *   - orders/details/fetch.js
 *   - orders/row-expand/open-close.js
 *   - js/dynamic/cache.js
 */

/**
 * Build a Bootstrap spinner element for an order detail load.
 *
 * @param {string|number} order_id - Order / vitrine id used in the element id.
 * @returns {HTMLDivElement} Spinner wrapper ready to append to the DOM.
 */
function add_spinner(order_id)
{

    var main_div = document.createElement("div");
    var inner_div = document.createElement("div");
    var text_span = document.createElement("span");

    main_div.className = "order-spinner d-flex justify-content-center align-items-center gap-2";
    main_div.setAttribute("id", "order-spinner-" + order_id);
    main_div.setAttribute("role", "status");
    main_div.setAttribute("aria-live", "polite");

    inner_div.className = "spinner-border";
    inner_div.setAttribute("aria-hidden", "true");

    text_span.className = "order-spinner-text";
    text_span.textContent = "Зареждане на поръчка";

    main_div.appendChild(inner_div);
    main_div.appendChild(text_span);

    return main_div;

}

/**
 * Remove the loading spinner for a given order, if present.
 *
 * @param {string|number} order_id - Order / vitrine id.
 * @returns {void}
 */
function remove_spinner(order_id) {

    let spinner = document.getElementById("order-spinner-" + order_id);
    if (spinner)
    {
        spinner.remove();
    }

}

/**
 * Show or hide the fold (close) button under a hidden detail row.
 *
 * @param {string|number} order_id - Order / vitrine id.
 * @param {boolean} visible - When true, adds `.is-visible` to the close button.
 * @returns {void}
 */
function set_hidden_row_close_visible(order_id, visible) {
    const hiddenRow = document.getElementById("hidden-row-" + order_id);
    if (!hiddenRow) {
        return;
    }
    const closeBtn = hiddenRow.querySelector(".hidden-row-close");
    if (!closeBtn) {
        return;
    }
    closeBtn.classList.toggle("is-visible", Boolean(visible));
}
