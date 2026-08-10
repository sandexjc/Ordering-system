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
    message.textContent = "⚠️ Грешка при зареждане на детайлите на поръчката...";
    wrapper.appendChild(message);

    const retryBtn = document.createElement("button");
    retryBtn.className = "btn btn-sm btn-outline-primary";
    retryBtn.textContent = "Опитай отново";
    retryBtn.addEventListener("click", () => retry_order(order_id));
    wrapper.appendChild(retryBtn);

    return wrapper;
}
