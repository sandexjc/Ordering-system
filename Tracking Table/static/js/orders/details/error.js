/*
 * orders/details/error.js
 * -----------------------
 * Error + retry UI when expanded order details fail to load.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on (runtime):
 *   - orders/details/fetch.js → retry_order
 *
 * Used by:
 *   - orders/details/fetch.js (get_order catch path)
 */

/**
 * Build an "error + retry" block for a failed order-detail fetch.
 *
 * @param {string|number} order_id - Order / vitrine id (used for element id and retry).
 * @returns {HTMLDivElement} Wrapper element (append to the hidden-table container).
 */
function create_order_error(order_id)
{
    const wrapper = document.createElement("div");
    wrapper.id = `order-error-${order_id}`;
    wrapper.style.textAlign = "center";
    wrapper.style.padding = "10px";

    const message = document.createElement("h6");
    message.style.color = "red";
    message.textContent = "⚠️ Грешка при зареждане на детайлите на поръчката...";
    wrapper.appendChild(message);

    const retryBtn = document.createElement("button");
    retryBtn.className = "btn btn-sm btn-outline-primary";
    retryBtn.textContent = "Опитай отново";
    retryBtn.addEventListener("click", () => retry_order(order_id));
    wrapper.appendChild(retryBtn);

    return wrapper;
}
