/**
 * Initial functions call
 */

/** Minimum required viewport width for user-list page is 600 px */
const MIN_VIEWPORT_WIDTH = 600;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

document.querySelectorAll(".send-password-email-form").forEach(bind_send_password_email_form);
document.querySelectorAll(".user-active-form").forEach(bind_user_active_form);
bind_user_role_change();
bind_user_list_email_column();

/**
 * Collapse / expand the email column from the header control.
 *
 * @returns {void}
 */
function bind_user_list_email_column()
{
    const table = document.querySelector(".user-list-table");
    const toggle = document.querySelector(".user-list-email-toggle");
    if (!table || !toggle)
    {
        return;
    }
    toggle.addEventListener("click", function () {
        const collapsed = table.classList.toggle("is-email-collapsed");
        toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
    });
}

/**
 * Confirm activate / deactivate over AJAX.
 * Closes the modal, shows a spinner on the row button, then a check or cross.
 * Updates the row without a page reload.
 *
 * @param {HTMLFormElement} form
 * @returns {void}
 */
function bind_user_active_form(form)
{
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const status_button_id = form.getAttribute("data-status-button");
        const button = status_button_id && document.getElementById(status_button_id);
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
        button.setAttribute("data-restore-html", button.innerHTML);
        button.setAttribute(
            "data-restore-kind",
            button.classList.contains("btn-danger") ? "danger" : "primary"
        );
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
                    throw new Error("set-active failed");
                }
                return response.json();
            })
            .then(function (data) {
                if (!data || !data.ok)
                {
                    throw new Error("set-active rejected");
                }
                set_user_active_result(button, form, true, Boolean(data.is_active));
            })
            .catch(function () {
                set_user_active_result(button, form, false, null);
            });
    });
}

/**
 * @param {HTMLButtonElement} button
 * @param {HTMLFormElement} form
 * @param {boolean} ok
 * @param {boolean|null} is_active
 * @returns {void}
 */
function set_user_active_result(button, form, ok, is_active)
{
    switch_send_password_email_state(button, function () {
        button.classList.remove("btn-primary", "btn-success", "btn-danger");
        button.classList.add(ok ? "btn-success" : "btn-danger");
        button.innerHTML = ok ? SEND_PASSWORD_EMAIL_CHECK_ICON : SEND_PASSWORD_EMAIL_CROSS_ICON;
        button.removeAttribute("aria-busy");
    });
    window.setTimeout(function () {
        switch_send_password_email_state(button, function () {
            if (ok)
            {
                apply_user_active_state(button, form, is_active);
            }
            else
            {
                restore_user_active_button(button);
            }
            button.disabled = false;
        });
    }, ok ? 7000 : 5000);
}

/**
 * @param {HTMLButtonElement} button
 * @param {HTMLFormElement} form
 * @param {boolean} is_active
 * @returns {void}
 */
function apply_user_active_state(button, form, is_active)
{
    const row = button.closest("tr");
    const active_cell = row && row.querySelector(".user-list-active-cell");
    if (active_cell)
    {
        active_cell.textContent = is_active ? "Да" : "Не";
    }
    button.classList.remove("btn-success", "btn-danger", "btn-primary");
    button.classList.add(is_active ? "btn-danger" : "btn-primary");
    button.textContent = is_active ? "Деактивирай" : "Активирай";
    const activate_input = form.querySelector("[name=activate]");
    if (activate_input)
    {
        activate_input.value = is_active ? "0" : "1";
    }
    const confirm_text = form.querySelector(".user-active-confirm-text");
    if (confirm_text)
    {
        const username = form.getAttribute("data-username") || "";
        const prefix = is_active
            ? "Сигурни ли сте, че искате да деактивирате този потребител: "
            : "Сигурни ли сте, че искате да активирате този потребител: ";
        confirm_text.replaceChildren(
            document.createTextNode(prefix),
            Object.assign(document.createElement("strong"), { textContent: username }),
            document.createTextNode("?")
        );
    }
    const submit = form.querySelector("button[type=submit]");
    if (submit)
    {
        submit.classList.remove("btn-danger", "btn-primary");
        submit.classList.add(is_active ? "btn-danger" : "btn-primary");
        submit.textContent = is_active ? "Деактивирай" : "Активирай";
    }
}

/**
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function restore_user_active_button(button)
{
    button.classList.remove("btn-success", "btn-danger", "btn-primary");
    button.classList.add(button.getAttribute("data-restore-kind") === "danger" ? "btn-danger" : "btn-primary");
    button.innerHTML = button.getAttribute("data-restore-html") || "";
}

/**
 * Role dropdown: confirm modal, then AJAX with spinner on the cell.
 *
 * @returns {void}
 */
function bind_user_role_change()
{
    const table = document.querySelector(".user-list-table");
    const modal = document.getElementById("user-role-confirm-modal");
    const form = document.getElementById("user-role-confirm-form");
    if (!table || !modal || !form)
    {
        return;
    }

    let pending_select = null;
    let submit_started = false;

    table.addEventListener("change", function (event) {
        const select = event.target.closest(".user-role-select");
        if (!select || select.disabled)
        {
            return;
        }
        if (select.value === select.getAttribute("data-current-role"))
        {
            return;
        }
        pending_select = select;
        submit_started = false;
        form.action = select.getAttribute("data-url");
        document.getElementById("user-role-confirm-role").value = select.value;
        const confirm_text = form.querySelector(".user-role-confirm-text");
        const username = select.getAttribute("data-username") || "";
        const role_label = select.options[select.selectedIndex]
            ? select.options[select.selectedIndex].text
            : select.value;
        confirm_text.replaceChildren(
            document.createTextNode("Сигурни ли сте, че искате да промените групата на потребител "),
            Object.assign(document.createElement("strong"), { textContent: username }),
            document.createTextNode(" на "),
            Object.assign(document.createElement("strong"), { textContent: role_label }),
            document.createTextNode("?")
        );
        if (window.bootstrap && bootstrap.Modal)
        {
            bootstrap.Modal.getOrCreateInstance(modal).show();
        }
    });

    modal.addEventListener("hidden.bs.modal", function () {
        if (!submit_started && pending_select)
        {
            pending_select.value = pending_select.getAttribute("data-current-role");
        }
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        if (!pending_select)
        {
            return;
        }
        submit_started = true;
        if (window.bootstrap && bootstrap.Modal)
        {
            const modal_instance = bootstrap.Modal.getInstance(modal) || bootstrap.Modal.getOrCreateInstance(modal);
            modal_instance.hide();
        }
        const wrapper = pending_select.closest(".user-role-status");
        const select = pending_select;
        const new_role = form.querySelector("[name=role]").value;
        set_user_role_busy(wrapper, select);
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
                    throw new Error("set-role failed");
                }
                return response.json();
            })
            .then(function (data) {
                if (!data || !data.ok)
                {
                    throw new Error("set-role rejected");
                }
                set_user_role_result(wrapper, select, true, data.role || new_role);
            })
            .catch(function () {
                set_user_role_result(wrapper, select, false, null);
            });
    });
}

/**
 * @param {HTMLElement} wrapper
 * @param {HTMLSelectElement} select
 * @returns {void}
 */
function set_user_role_busy(wrapper, select)
{
    select.hidden = true;
    select.disabled = true;
    let feedback = wrapper.querySelector(".user-role-feedback");
    if (!feedback)
    {
        feedback = document.createElement("span");
        feedback.className = "user-role-feedback btn btn-sm btn-primary";
        wrapper.appendChild(feedback);
    }
    feedback.hidden = false;
    switch_send_password_email_state(feedback, function () {
        feedback.classList.remove("btn-success", "btn-danger");
        feedback.classList.add("btn-primary");
        feedback.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    });
}

/**
 * @param {HTMLElement} wrapper
 * @param {HTMLSelectElement} select
 * @param {boolean} ok
 * @param {string|null} role
 * @returns {void}
 */
function set_user_role_result(wrapper, select, ok, role)
{
    const feedback = wrapper.querySelector(".user-role-feedback");
    if (!feedback)
    {
        restore_user_role_select(wrapper, select, ok, role);
        return;
    }
    switch_send_password_email_state(feedback, function () {
        feedback.classList.remove("btn-primary", "btn-success", "btn-danger");
        feedback.classList.add(ok ? "btn-success" : "btn-danger");
        feedback.innerHTML = ok ? SEND_PASSWORD_EMAIL_CHECK_ICON : SEND_PASSWORD_EMAIL_CROSS_ICON;
    });
    window.setTimeout(function () {
        switch_send_password_email_state(feedback, function () {
            restore_user_role_select(wrapper, select, ok, role);
        });
    }, ok ? 7000 : 5000);
}

/**
 * @param {HTMLElement} wrapper
 * @param {HTMLSelectElement} select
 * @param {boolean} ok
 * @param {string|null} role
 * @returns {void}
 */
function restore_user_role_select(wrapper, select, ok, role)
{
    const feedback = wrapper.querySelector(".user-role-feedback");
    if (feedback)
    {
        feedback.hidden = true;
        feedback.innerHTML = "";
        feedback.classList.remove("btn-success", "btn-danger");
        feedback.classList.add("btn-primary");
    }
    if (ok && role)
    {
        select.setAttribute("data-current-role", role);
        select.value = role;
    }
    else
    {
        select.value = select.getAttribute("data-current-role");
    }
    select.hidden = false;
    select.disabled = false;
}
