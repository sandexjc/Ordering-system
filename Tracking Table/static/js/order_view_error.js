/**
 * This function builds "error + retry" view and returns a DocumentFragment.
 * @param {*} order_id 
 */
function create_order_error(order_id) 
{
    const wrapper = document.createElement("div");
    wrapper.id = `order-error-${order_id}`;
    wrapper.style.textAlign = "center";
    wrapper.style.padding = "10px";

    const message = document.createElement("h6");
    message.style.color = "red";
    message.textContent = "⚠️ Could not load order details...";
    wrapper.appendChild(message);

    const retryBtn = document.createElement("button");
    retryBtn.className = "btn btn-sm btn-outline-primary";
    retryBtn.textContent = "🔄 Retry";
    retryBtn.addEventListener("click", () => retry_order(order_id));
    wrapper.appendChild(retryBtn);

    return wrapper;
}
