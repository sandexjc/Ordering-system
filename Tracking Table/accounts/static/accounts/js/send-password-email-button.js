/**
 * Submit a password-reset email form over AJAX.
 * Shows a spinner until the response, then a green check (7s) or red cross (5s).
 *
 * @param {HTMLFormElement} form
 * @returns {void}
 */
function bind_send_password_email_form(form)
{
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const status_button_id = form.getAttribute("data-status-button");
        const button = (status_button_id && document.getElementById(status_button_id))
            || form.querySelector("button[type=submit]");
        if (!button || button.disabled)
        {
            return;
        }
        const modal = form.closest(".modal");
        if (modal && window.bootstrap && bootstrap.Modal)
        {
            const modal_instance = bootstrap.Modal.getInstance(modal) || bootstrap.Modal.getOrCreateInstance(modal);
            modal_instance.hide();
        }
        const original_html = button.getAttribute("data-original-html") || button.innerHTML;
        button.setAttribute("data-original-html", original_html);
        set_send_password_email_busy(button);
        const csrf = form.querySelector("[name=csrfmiddlewaretoken]");
        fetch(form.action, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrf ? csrf.value : "",
            },
            body: new FormData(form),
        })
            .then(function (response) {
                if (!response.ok)
                {
                    throw new Error("send failed");
                }
                return response.json();
            })
            .then(function (data) {
                set_send_password_email_result(button, Boolean(data && data.ok), original_html);
            })
            .catch(function () {
                set_send_password_email_result(button, false, original_html);
            });
    });
}

/**
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function set_send_password_email_busy(button)
{
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    switch_send_password_email_state(button, function () {
        button.classList.remove("btn-success", "btn-danger");
        button.classList.add("btn-primary");
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    });
}

/**
 * @param {HTMLButtonElement} button
 * @param {boolean} ok
 * @param {string} original_html
 * @returns {void}
 */
function set_send_password_email_result(button, ok, original_html)
{
    switch_send_password_email_state(button, function () {
        button.classList.remove("btn-primary", "btn-success", "btn-danger");
        button.classList.add(ok ? "btn-success" : "btn-danger");
        button.innerHTML = ok ? SEND_PASSWORD_EMAIL_CHECK_ICON : SEND_PASSWORD_EMAIL_CROSS_ICON;
        button.removeAttribute("aria-busy");
    });
    window.setTimeout(function () {
        switch_send_password_email_state(button, function () {
            button.classList.remove("btn-success", "btn-danger");
            button.classList.add("btn-primary");
            button.innerHTML = original_html;
            button.disabled = false;
        });
    }, ok ? 7000 : 5000);
}

/**
 * Fade the button, swap its appearance, then fade back in.
 *
 * @param {HTMLButtonElement} button
 * @param {function(): void} apply_state
 * @returns {void}
 */
function switch_send_password_email_state(button, apply_state)
{
    button.classList.add("is-switching");
    window.setTimeout(function () {
        apply_state();
        button.classList.remove("is-switching");
    }, 180);
}

const SEND_PASSWORD_EMAIL_CHECK_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg>';
const SEND_PASSWORD_EMAIL_CROSS_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>';
