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
bind_user_list_helper_rows();

/**
 * Active toast instance for helper action feedback.
 *
 * @type {bootstrap.Toast|null}
 */
let active_user_list_toast = null;
show_user_list_toast_from_alert();

/**
 * Bind row unfold/fold behavior with orders-like height transitions.
 *
 * @returns {void}
 */
function bind_user_list_helper_rows()
{
    const table = document.querySelector(".user-list-table .table");
    if (!table)
    {
        return;
    }
    table.addEventListener("click", function (event) {
        const main_row = event.target.closest(".user-list-main-row");
        if (!main_row || !table.contains(main_row))
        {
            return;
        }
        const row_id = main_row.getAttribute("data-user-row-id");
        if (!row_id)
        {
            return;
        }
        const helper_row = table.querySelector('.user-list-helper-row[data-user-row-id="' + row_id + '"]');
        const helper_inner = helper_row && helper_row.querySelector(".user-list-helper-inner");
        if (!helper_row || !helper_inner)
        {
            return;
        }
        if (helper_inner._isOpen)
        {
            close_user_list_helper_row(main_row, helper_row, helper_inner);
        }
        else
        {
            open_user_list_helper_row(main_row, helper_row, helper_inner);
        }
    });

    table.querySelectorAll(".user-list-main-row").forEach(function (main_row) {
        const row_id = main_row.getAttribute("data-user-row-id");
        if (!row_id)
        {
            return;
        }
        const helper_row = table.querySelector('.user-list-helper-row[data-user-row-id="' + row_id + '"]');
        const helper_inner = helper_row && helper_row.querySelector(".user-list-helper-inner");
        if (!helper_row || !helper_inner)
        {
            return;
        }
        helper_inner.style.display = "none";
        helper_inner.style.height = "0px";
        helper_inner.style.opacity = "0";
        helper_inner.classList.remove("is-open");
        helper_inner._isOpen = false;
        helper_inner._isClosing = false;
        if (helper_inner._closeTimeoutId)
        {
            window.clearTimeout(helper_inner._closeTimeoutId);
            helper_inner._closeTimeoutId = null;
        }
        main_row.classList.remove("is-expanded");
        main_row.setAttribute("aria-expanded", "false");
        helper_row.setAttribute("aria-hidden", "true");
    });
}

/**
 * @param {HTMLElement} helper_inner
 * @returns {void}
 */
function cancel_pending_helper_transition(helper_inner)
{
    if (helper_inner._closeTimeoutId)
    {
        window.clearTimeout(helper_inner._closeTimeoutId);
        helper_inner._closeTimeoutId = null;
    }
}

/**
 * @param {HTMLElement} main_row
 * @param {HTMLElement} helper_row
 * @param {HTMLElement} helper_inner
 * @returns {void}
 */
function open_user_list_helper_row(main_row, helper_row, helper_inner)
{
    cancel_pending_helper_transition(helper_inner);
    helper_inner._isClosing = false;
    helper_inner.style.display = "block";
    helper_inner.style.height = "auto";
    helper_inner.style.opacity = "0";
    requestAnimationFrame(function () {
        helper_inner.classList.add("is-open");
        helper_inner.style.opacity = "1";
    });
    helper_inner._isOpen = true;
    main_row.classList.add("is-expanded");
    main_row.setAttribute("aria-expanded", "true");
    helper_row.setAttribute("aria-hidden", "false");
}

/**
 * @param {HTMLElement} main_row
 * @param {HTMLElement} helper_row
 * @param {HTMLElement} helper_inner
 * @returns {void}
 */
function close_user_list_helper_row(main_row, helper_row, helper_inner)
{
    cancel_pending_helper_transition(helper_inner);
    helper_inner._isClosing = true;
    helper_inner.classList.remove("is-open");
    helper_inner.style.opacity = "0";
    helper_inner._isOpen = false;
    helper_inner._closeTimeoutId = window.setTimeout(function () {
        helper_inner.style.display = "none";
        helper_inner.style.height = "0px";
        helper_inner._isClosing = false;
        helper_inner._closeTimeoutId = null;
    }, 170);
    main_row.classList.remove("is-expanded");
    main_row.setAttribute("aria-expanded", "false");
    helper_row.setAttribute("aria-hidden", "true");
}

/**
 * @param {string} message
 * @param {"success"|"error"} type
 * @returns {void}
 */
function show_user_list_toast(message, type)
{
    const toast_el = document.getElementById("user-list-toast");
    const toast_body = document.getElementById("user-list-toast-body");
    if (!toast_el || !toast_body || !window.bootstrap || !bootstrap.Toast)
    {
        return;
    }
    if (active_user_list_toast)
    {
        active_user_list_toast.hide();
    }
    toast_el.classList.remove("bg-success", "bg-danger");
    toast_el.classList.add(type === "success" ? "bg-success" : "bg-danger");
    toast_body.textContent = message;
    active_user_list_toast = new bootstrap.Toast(toast_el, {
        delay: type === "success" ? 2500 : 9000,
        autohide: true,
    });
    active_user_list_toast.show();
}

/**
 * Convert Django page alert messages into toast on user-list page.
 *
 * @returns {void}
 */
function show_user_list_toast_from_alert()
{
    const alert_el = document.querySelector(".auto-dismiss-alert");
    if (!alert_el)
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
    show_user_list_toast(message, is_error ? "error" : "success");
    alert_el.style.display = "none";
}

window.on_user_list_send_password_email_result = function (form, ok) {
    const username = form.getAttribute("data-username") || "";
    if (ok)
    {
        show_user_list_toast("Изпратен е имейл за смяна на паролата на " + username + ".", "success");
    }
    else
    {
        show_user_list_toast("Имейлът за смяна на паролата на " + username + " не беше изпратен.", "error");
    }
};

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
                return response.json()
                    .catch(function () { return null; })
                    .then(function (payload) {
                        return {
                            response_ok: response.ok,
                            payload: payload,
                        };
                    });
            })
            .then(function (result) {
                const data = result.payload;
                if (!result.response_ok || !data || !data.ok)
                {
                    throw new Error((data && data.error) || "Възникна грешка при промяна на активността.");
                }
                set_user_active_result(button, form, true, Boolean(data.is_active));
                const username = form.getAttribute("data-username") || "";
                show_user_list_toast(
                    "Потребителят " + username + (data.is_active ? " е активиран." : " е деактивиран."),
                    "success"
                );
            })
            .catch(function (error) {
                set_user_active_result(button, form, false, null);
                show_user_list_toast(error && error.message ? error.message : "Промяната на активността не беше успешна.", "error");
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
    }, ok ? 2000 : 5000);
}

/**
 * @param {HTMLButtonElement} button
 * @param {HTMLFormElement} form
 * @param {boolean} is_active
 * @returns {void}
 */
function apply_user_active_state(button, form, is_active)
{
    const helper_row = button.closest(".user-list-helper-row");
    const row_id = helper_row && helper_row.getAttribute("data-user-row-id");
    const active_cell = row_id && document.getElementById("user-list-active-cell-" + row_id);
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
                return response.json()
                    .catch(function () { return null; })
                    .then(function (payload) {
                        return {
                            response_ok: response.ok,
                            payload: payload,
                        };
                    });
            })
            .then(function (result) {
                const data = result.payload;
                if (!result.response_ok || !data || !data.ok)
                {
                    throw new Error((data && data.error) || "Възникна грешка при промяна на групата.");
                }
                set_user_role_result(wrapper, select, true, data.role || new_role);
                const role_label = select.options[select.selectedIndex]
                    ? select.options[select.selectedIndex].text
                    : (data.role || new_role);
                show_user_list_toast(
                    "Групата на " + (select.getAttribute("data-username") || "") + " е променена на " + role_label + ".",
                    "success"
                );
            })
            .catch(function (error) {
                set_user_role_result(wrapper, select, false, null);
                show_user_list_toast(error && error.message ? error.message : "Промяната на групата не беше успешна.", "error");
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
    }, ok ? 2000 : 5000);
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
