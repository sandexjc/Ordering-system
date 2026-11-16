/**
 * Initial functions call
 */

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

const profile_appearance_form = document.getElementById("profile-appearance-form");
if (profile_appearance_form)
{
    profile_appearance_form.querySelectorAll("[name=theme], [name=background], [name=accent], [name=text_size], [name=row_density], [name=reduced_motion]").forEach(function (input) {
        input.addEventListener("change", preview_profile_appearance);
    });
    profile_appearance_form.addEventListener("submit", save_profile_appearance);
}

const profile_devices = document.getElementById("profile-devices");
const profile_device_list = document.getElementById("profile-device-list");
const profile_device_send_form = document.getElementById("profile-device-send-form");
const profile_device_modal = document.getElementById("profile-device-modal");
const profile_device_qr = document.getElementById("profile-device-qr");
const profile_device_email = document.getElementById("profile-device-email");
const profile_device_email_html = profile_device_email ? profile_device_email.innerHTML : "";
let profile_device_picture_request = null;
let profile_device_picture_url = "";
let profile_device_can_email = false;
if (profile_devices && profile_device_send_form)
{
    load_profile_devices();
    if (profile_device_modal)
    {
        profile_device_modal.addEventListener("show.bs.modal", open_profile_device_modal);
        profile_device_modal.addEventListener("hidden.bs.modal", reset_profile_device_modal);
    }
    if (profile_device_email)
    {
        profile_device_email.addEventListener("click", send_profile_device_email);
    }
    bind_profile_device_revoke_confirm();
}

/**
 * @param {Event} event
 * @returns {void}
 */
function save_profile_details(event)
{
    event.preventDefault();
    const button = document.getElementById("profile-details-save");
    submit_profile_form(profile_details_form, button, null, function (ok, data) {
        if (!ok)
        {
            show_profile_toast(
                (data && data.error) || "Профилът не беше запазен.",
                "error"
            );
        }
    });
}

/**
 * @param {HTMLFormElement} form
 * @param {string} name
 * @param {string[]} allowed
 * @param {string} attribute
 * @returns {void}
 */
function preview_profile_choice(form, name, allowed, attribute)
{
    const input = form.querySelector("[name=" + name + "]");
    if (!input || allowed.indexOf(input.value) === -1)
    {
        return;
    }
    document.documentElement.setAttribute(attribute, input.value);
}

/**
 * @returns {void}
 */
function preview_profile_appearance()
{
    preview_profile_choice(profile_appearance_form, "theme", ["light", "dark"], "data-bs-theme");
    preview_profile_choice(
        profile_appearance_form,
        "background",
        ["city", "plain", "warm_paper", "blue", "green", "sand", "slate"],
        "data-bg"
    );
    preview_profile_choice(
        profile_appearance_form,
        "accent",
        ["stone", "blue", "teal", "sand", "indigo", "rose", "orange", "slate", "clear"],
        "data-accent"
    );
    preview_profile_choice(
        profile_appearance_form,
        "text_size",
        ["small", "medium", "large"],
        "data-text"
    );
    preview_profile_choice(
        profile_appearance_form,
        "row_density",
        ["standard", "compact", "dense"],
        "data-density"
    );
    preview_profile_choice(
        profile_appearance_form,
        "reduced_motion",
        ["off", "reduce"],
        "data-motion"
    );
}

/**
 * @param {Event} event
 * @returns {void}
 */
function save_profile_appearance(event)
{
    event.preventDefault();
    const button = document.getElementById("profile-appearance-save");
    submit_profile_form(profile_appearance_form, button, null, function (ok) {
        show_profile_toast(
            ok ? "Настройките за външен вид са запазени." : "Настройките не бяха запазени.",
            ok ? "success" : "error"
        );
    });
}

/**
 * @returns {void}
 */
function open_profile_device_modal()
{
    reset_profile_device_modal();
    const controller = new AbortController();
    profile_device_picture_request = controller;
    const csrf = profile_device_send_form.querySelector("[name=csrfmiddlewaretoken]");
    fetch(profile_devices.getAttribute("data-qr-url"), {
        method: "POST",
        credentials: "same-origin",
        signal: controller.signal,
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf ? csrf.value : "",
        },
    })
        .then(function (response) {
            const content_type = response.headers.get("Content-Type") || "";
            if (!response.ok || content_type.indexOf("image/svg+xml") !== 0)
            {
                throw new Error("picture failed");
            }
            const can_email = response.headers.get("X-Can-Email") === "1";
            return response.blob().then(function (blob) {
                return { blob: blob, can_email: can_email };
            });
        })
        .then(function (result) {
            if (profile_device_picture_request !== controller)
            {
                return;
            }
            // The picture is an image response. Keep it out of the page HTML.
            profile_device_picture_url = URL.createObjectURL(result.blob);
            const image = document.createElement("img");
            image.alt = "Код за добавяне на устройство";
            image.src = profile_device_picture_url;
            profile_device_qr.innerHTML = "";
            profile_device_qr.appendChild(image);
            profile_device_can_email = result.can_email;
            profile_device_email.disabled = !result.can_email;
            if (result.can_email)
            {
                profile_device_email.removeAttribute("title");
            }
            else
            {
                profile_device_email.title = "Няма въведен имейл.";
            }
        })
        .catch(function (error) {
            if (error && error.name === "AbortError")
            {
                return;
            }
            if (profile_device_picture_request !== controller)
            {
                return;
            }
            show_profile_device_qr_message("Кодът не може да бъде зареден.");
        });
}

/**
 * @returns {void}
 */
function reset_profile_device_modal()
{
    if (profile_device_picture_request)
    {
        profile_device_picture_request.abort();
        profile_device_picture_request = null;
    }
    if (profile_device_picture_url)
    {
        URL.revokeObjectURL(profile_device_picture_url);
        profile_device_picture_url = "";
    }
    profile_device_can_email = false;
    if (profile_device_qr)
    {
        profile_device_qr.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Зареждане</span></div>';
    }
    if (profile_device_email)
    {
        profile_device_email.innerHTML = profile_device_email_html;
        profile_device_email.disabled = true;
        profile_device_email.removeAttribute("aria-busy");
        profile_device_email.removeAttribute("title");
    }
}

/**
 * @param {string} message
 * @returns {void}
 */
function show_profile_device_qr_message(message)
{
    profile_device_qr.innerHTML = "";
    const note = document.createElement("p");
    note.className = "profile-device-qr-message";
    note.textContent = message;
    profile_device_qr.appendChild(note);
}

/**
 * @returns {void}
 */
function send_profile_device_email()
{
    if (!profile_device_email || profile_device_email.disabled)
    {
        return;
    }
    profile_device_email.disabled = true;
    profile_device_email.setAttribute("aria-busy", "true");
    profile_device_email.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    const csrf = profile_device_send_form.querySelector("[name=csrfmiddlewaretoken]");
    fetch(profile_devices.getAttribute("data-send-url"), {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf ? csrf.value : "",
        },
        body: new FormData(profile_device_send_form),
    })
        .then(function (response) {
            return response.json().then(function (data) {
                return { failed: !response.ok, data: data };
            });
        })
        .then(function (result) {
            const ok = !result.failed && Boolean(result.data && result.data.ok);
            if (ok)
            {
                const modal = bootstrap.Modal.getInstance(profile_device_modal) || bootstrap.Modal.getOrCreateInstance(profile_device_modal);
                modal.hide();
                show_profile_toast("Имейлът за добавяне на устройство е изпратен.", "success");
                return;
            }
            finish_profile_device_email(false);
        })
        .catch(function () {
            finish_profile_device_email(false);
        });
}

/**
 * @param {boolean} ok
 * @returns {void}
 */
function finish_profile_device_email(ok)
{
    if (profile_device_email)
    {
        profile_device_email.innerHTML = profile_device_email_html;
        profile_device_email.disabled = !profile_device_can_email;
        profile_device_email.removeAttribute("aria-busy");
    }
    if (!ok)
    {
        show_profile_toast("Имейлът не беше изпратен.", "error");
    }
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
            return response.json().then(function (data) {
                return { failed: !response.ok, data: data };
            });
        })
        .then(function (result) {
            const data = result.data;
            const ok = !result.failed && Boolean(data && data.ok);
            set_profile_button_result(button, ok, original_html);
            if (on_result)
            {
                on_result(ok, data);
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
            open_profile_device_revoke_confirm(device, button);
        });

        row.appendChild(text);
        row.appendChild(button);
        profile_device_list.appendChild(row);
    });
}

let pending_profile_device_revoke = null;

/**
 * @returns {void}
 */
function bind_profile_device_revoke_confirm()
{
    const modal = document.getElementById("profile-device-revoke-confirm");
    const confirm_button = document.getElementById("profile-device-revoke-confirm-submit");
    if (!modal || !confirm_button)
    {
        return;
    }
    confirm_button.addEventListener("click", function () {
        const pending = pending_profile_device_revoke;
        if (!pending)
        {
            return;
        }
        pending_profile_device_revoke = null;
        if (window.bootstrap && bootstrap.Modal)
        {
            const modal_instance = bootstrap.Modal.getInstance(modal) || bootstrap.Modal.getOrCreateInstance(modal);
            modal_instance.hide();
        }
        revoke_profile_device(pending.url, pending.button);
    });
    modal.addEventListener("hidden.bs.modal", function () {
        pending_profile_device_revoke = null;
    });
}

/**
 * @param {{device_name: string, revoke_url: string}} device
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function open_profile_device_revoke_confirm(device, button)
{
    if (button.disabled)
    {
        return;
    }
    const modal = document.getElementById("profile-device-revoke-confirm");
    if (!modal || !window.bootstrap || !bootstrap.Modal)
    {
        return;
    }
    pending_profile_device_revoke = {
        url: device.revoke_url,
        button: button,
    };
    const confirm_text = modal.querySelector(".device-revoke-confirm-text");
    if (confirm_text)
    {
        confirm_text.replaceChildren(
            document.createTextNode("Сигурни ли сте, че искате да премахнете това устройство: "),
            Object.assign(document.createElement("strong"), { textContent: device.device_name || "" }),
            document.createTextNode("?")
        );
    }
    bootstrap.Modal.getOrCreateInstance(modal).show();
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
