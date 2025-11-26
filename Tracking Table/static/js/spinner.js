/**
 * Function to create HTML spinner element and return it
 */
function add_spinner(order_id)
{

    var main_div = document.createElement("div");
    var inner_div = document.createElement("div");

    main_div.className = "d-flex justify-content-center";
    main_div.setAttribute("id", "order-spinner-" + order_id);

    inner_div.className = "spinner-border";
    inner_div.setAttribute("role", "status");

    main_div.appendChild(inner_div);

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