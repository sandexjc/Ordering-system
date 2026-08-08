/**
 * Function to create HTML spinner element and return it
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
 * Function to remove HTML spinner element from specified element
 */
function remove_spinner(order_id) {

    let spinner = document.getElementById("order-spinner-" + order_id);
    if (spinner)
    {
        spinner.remove();
    }
    
}

/**
 * Show or hide the fold button under a hidden row.
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
