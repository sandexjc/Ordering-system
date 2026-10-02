/**
 * Initial functions call
 */

/** Minimum required viewport width for create-user page is 600 px */
const MIN_VIEWPORT_WIDTH = 600;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

setup_create_user_form();
show_create_user_toast_from_alert();

/**
 * Show a spinner while submit is in-flight.
 *
 * @returns {void}
 */
function setup_create_user_form()
{
    const form = document.getElementById("create-user-form");
    const submit_btn = document.getElementById("create-user-submit-btn");
    if (!form || !submit_btn)
    {
        return;
    }
    const label = submit_btn.querySelector(".btn-label");
    const spinner = submit_btn.querySelector(".spinner-border");
    form.addEventListener("submit", function () {
        submit_btn.disabled = true;
        if (label)
        {
            label.classList.add("d-none");
        }
        if (spinner)
        {
            spinner.classList.remove("d-none");
        }
    });
}

/**
 * Convert page alert messages to a toast on this screen.
 *
 * @returns {void}
 */
function show_create_user_toast_from_alert()
{
    const alert_el = document.querySelector(".auto-dismiss-alert");
    const toast_el = document.getElementById("create-user-toast");
    const toast_body = document.getElementById("create-user-toast-body");
    if (!alert_el || !toast_el || !toast_body || !window.bootstrap || !bootstrap.Toast)
    {
        return;
    }
    const message_el = alert_el.querySelector(".text-center");
    const message = message_el ? message_el.textContent.trim() : alert_el.textContent.trim();
    if (!message)
    {
        return;
    }
    const is_error = alert_el.classList.contains("alert-danger");
    toast_el.classList.remove("bg-success", "bg-danger");
    toast_el.classList.add(is_error ? "bg-danger" : "bg-success");
    toast_body.textContent = message;
    alert_el.style.display = "none";
    const toast = bootstrap.Toast.getOrCreateInstance(toast_el, {
        delay: 2000,
        autohide: true,
    });
    toast.show();
}