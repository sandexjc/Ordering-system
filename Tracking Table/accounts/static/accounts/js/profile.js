/**
 * Initial functions call
 */

/** Minimum required viewport width for profile page is 600 px */
const MIN_VIEWPORT_WIDTH = 600;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

const PROFILE_CHECK_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg>';
const PROFILE_CROSS_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>';
const PROFILE_RESULT_MS = 3000;

document.querySelectorAll(".profile-section-toggle").forEach(function (button) {
    button.addEventListener("click", function () {
        const section = button.closest(".profile-section");
        const open = section.classList.toggle("is-open");
        button.setAttribute("aria-expanded", open ? "true" : "false");
    });
});

const profile_details_form = document.getElementById("profile-details-form");
if (profile_details_form)
{
    profile_details_form.addEventListener("submit", save_profile_details);
}

const profile_devices = document.getElementById("profile-devices");
const profile_device_list = document.getElementById("profile-device-list");
const profile_device_send_form = document.getElementById("profile-device-send-form");
if (profile_devices && profile_device_send_form)
{
    load_profile_devices();
    profile_device_send_form.addEventListener("submit", send_profile_device_email);
}

/**
 * @param {Event} event
 * @returns {void}
 */
function save_profile_details(event)
{
    event.preventDefault();
    const button = document.getElementById("profile-details-save");
    submit_profile_form(profile_details_form, button);
}

/**
 * @param {Event} event
 * @returns {void}
 */
function send_profile_device_email(event)
{
    event.preventDefault();
    const button = document.getElementById("profile-device-send");
    submit_profile_form(profile_device_send_form, button, profile_devices.getAttribute("data-send-url"), function (ok) {
        show_profile_toast(
            ok ? "Имейлът за добавяне на устройство е изпратен." : "Имейлът не беше изпратен.",
            ok ? "success" : "error"
        );
    });
}

/**
 * @param {HTMLFormElement} form
 * @param {HTMLButtonElement} button
 * @param {string|null} url
 * @param {function(boolean): void|null} on_result
 * @returns {void}
 */
function submit_profile_form(form, button, url, on_result)
{
    if (!button || button.disabled)
    {
        return;
    }
    const original_html = button.getAttribute("data-original-html") || button.innerHTML;
    button.setAttribute("data-original-html", original_html);
    set_profile_button_busy(button);
    const csrf = form.querySelector("[name=csrfmiddlewaretoken]");
    fetch(url || form.action, {
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
                throw new Error("request failed");
            }
            return response.json();
        })
        .then(function (data) {
            const ok = Boolean(data && data.ok);
            set_profile_button_result(button, ok, original_html);
            if (on_result)
            {
                on_result(ok);
            }
        })
        .catch(function () {
            set_profile_button_result(button, false, original_html);
            if (on_result)
            {
                on_result(false);
            }
        });
}

let active_profile_toast = null;

/**
 * @param {string} message
 * @param {"success"|"error"} type
 * @returns {void}
 */
function show_profile_toast(message, type)
{
    const toast_el = document.getElementById("profile-toast");
    const toast_body = document.getElementById("profile-toast-body");
    if (!toast_el || !toast_body || !window.bootstrap || !bootstrap.Toast)
    {
        return;
    }
    if (active_profile_toast)
    {
        active_profile_toast.hide();
    }
    toast_el.classList.remove("bg-success", "bg-danger");
    toast_el.classList.add(type === "success" ? "bg-success" : "bg-danger");
    toast_body.textContent = message;
    active_profile_toast = new bootstrap.Toast(toast_el, {
        delay: type === "success" ? 2500 : 9000,
        autohide: true,
    });
    active_profile_toast.show();
}

/**
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function set_profile_button_busy(button)
{
    if (!button.getAttribute("data-original-class"))
    {
        button.setAttribute("data-original-class", button.className);
    }
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    switch_profile_button_state(button, function () {
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
function set_profile_button_result(button, ok, original_html)
{
    switch_profile_button_state(button, function () {
        button.classList.remove("btn-primary", "btn-success", "btn-danger");
        button.classList.add(ok ? "btn-success" : "btn-danger");
        button.innerHTML = ok ? PROFILE_CHECK_ICON : PROFILE_CROSS_ICON;
        button.removeAttribute("aria-busy");
    });
    window.setTimeout(function () {
        switch_profile_button_state(button, function () {
        button.innerHTML = original_html;
        button.className = button.getAttribute("data-original-class") || button.className;
        button.disabled = false;
        });
    }, PROFILE_RESULT_MS);
}

/**
 * @param {HTMLButtonElement} button
 * @param {function(): void} apply_state
 * @returns {void}
 */
function switch_profile_button_state(button, apply_state)
{
    button.classList.add("is-switching");
    window.setTimeout(function () {
        apply_state();
        button.classList.remove("is-switching");
    }, 180);
}

/**
 * @returns {void}
 */
function load_profile_devices()
{
    fetch(profile_devices.getAttribute("data-list-url"), {
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
    })
        .then(function (response) {
            if (!response.ok)
            {
                throw new Error("list failed");
            }
            return response.json();
        })
        .then(function (data) {
            render_profile_devices(data.devices || []);
        })
        .catch(function () {
            profile_device_list.innerHTML = "";
            const empty = document.createElement("li");
            empty.className = "profile-device-empty";
            empty.textContent = "Устройствата не могат да бъдат заредени.";
            profile_device_list.appendChild(empty);
        });
}

/**
 * @param {Array} devices
 * @returns {void}
 */
function render_profile_devices(devices)
{
    profile_device_list.innerHTML = "";
    if (!devices.length)
    {
        const empty = document.createElement("li");
        empty.className = "profile-device-empty";
        empty.textContent = "Няма добавени устройства.";
        profile_device_list.appendChild(empty);
        return;
    }
    devices.forEach(function (device) {
        const row = document.createElement("li");
        row.className = "profile-device-row";

        const text = document.createElement("div");
        const name = document.createElement("strong");
        name.textContent = device.device_name;
        const meta = document.createElement("div");
        meta.className = "profile-device-meta";
        meta.textContent = "Последно използване: " + (device.last_used_at || "—");
        text.appendChild(name);
        text.appendChild(meta);

        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-sm btn-danger";
        button.textContent = "Премахни";
        button.addEventListener("click", function () {
            revoke_profile_device(device.revoke_url, button);
        });

        row.appendChild(text);
        row.appendChild(button);
        profile_device_list.appendChild(row);
    });
}

/**
 * @param {string} url
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function revoke_profile_device(url, button)
{
    if (button.disabled)
    {
        return;
    }
    const original_html = button.innerHTML;
    set_profile_button_busy(button);
    const csrf = profile_device_send_form.querySelector("[name=csrfmiddlewaretoken]");
    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf ? csrf.value : "",
        },
    })
        .then(function (response) {
            if (!response.ok)
            {
                throw new Error("revoke failed");
            }
            return response.json();
        })
        .then(function () {
            set_profile_button_result(button, true, original_html);
            window.setTimeout(load_profile_devices, PROFILE_RESULT_MS);
        })
        .catch(function () {
            set_profile_button_result(button, false, original_html);
        });
}
