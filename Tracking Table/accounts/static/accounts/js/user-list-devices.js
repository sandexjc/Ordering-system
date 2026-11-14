document.querySelectorAll(".user-list-helper-inner").forEach(function (helper_inner) {
    helper_inner.addEventListener("user-list-helper-open", function () {
        load_user_list_devices(helper_inner);
    });
});

let pending_user_list_device_send_form = null;
let pending_user_list_device_revoke_button = null;

document.addEventListener("click", function (event) {
    const revoke_button = event.target.closest(".user-list-device-revoke");
    if (revoke_button)
    {
        open_user_list_device_revoke_confirm(revoke_button);
        return;
    }
    const send_button = event.target.closest(".user-list-device-send");
    if (send_button)
    {
        open_user_list_device_email_confirm(send_button);
    }
});

bind_user_list_device_confirms();

document.addEventListener("submit", function (event) {
    const form = event.target.closest(".user-list-device-send-form");
    if (!form)
    {
        return;
    }
    event.preventDefault();
    send_user_list_device_email(form);
});

/**
 * @param {HTMLElement} helper_inner
 * @returns {void}
 */
function load_user_list_devices(helper_inner)
{
    const block = helper_inner.querySelector(".user-list-devices");
    if (!block)
    {
        return;
    }
    const list = block.querySelector(".user-list-device-list");
    fetch(block.getAttribute("data-list-url"), {
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
            render_user_list_devices(list, data.devices || []);
        })
        .catch(function () {
            show_user_list_toast("Устройствата не могат да бъдат заредени.", "error");
        });
}

/**
 * @param {HTMLElement} list
 * @param {Array} devices
 * @returns {void}
 */
function render_user_list_devices(list, devices)
{
    list.innerHTML = "";
    if (!devices.length)
    {
        const empty = document.createElement("li");
        empty.className = "user-list-device-meta";
        empty.textContent = "Няма добавени устройства.";
        list.appendChild(empty);
        return;
    }
    devices.forEach(function (device) {
        const row = document.createElement("li");
        row.className = "user-list-device-row";
        const text = document.createElement("div");
        const name = document.createElement("strong");
        name.textContent = device.device_name;
        const meta = document.createElement("div");
        meta.className = "user-list-device-meta";
        meta.textContent = "Последно използване: " + (device.last_used_at || "—");
        text.appendChild(name);
        text.appendChild(meta);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-sm btn-danger user-list-device-revoke";
        button.textContent = "Премахни";
        button.setAttribute("data-revoke-url", device.revoke_url);
        button.setAttribute("data-device-name", device.device_name || "");
        row.appendChild(text);
        row.appendChild(button);
        list.appendChild(row);
    });
}

/**
 * @param {HTMLFormElement} form
 * @returns {void}
 */
function send_user_list_device_email(form)
{
    const button = form.querySelector(".user-list-device-send");
    if (!button || button.disabled)
    {
        return;
    }
    button.disabled = true;
    const csrf = form.querySelector("[name=csrfmiddlewaretoken]");
    fetch(form.getAttribute("data-send-url"), {
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
            show_user_list_toast(
                data && data.ok ? "Имейлът за добавяне на устройство е изпратен." : "Имейлът не беше изпратен.",
                data && data.ok ? "success" : "error"
            );
        })
        .catch(function () {
            show_user_list_toast("Имейлът не беше изпратен.", "error");
        })
        .finally(function () {
            button.disabled = false;
        });
}

/**
 * @returns {void}
 */
function bind_user_list_device_confirms()
{
    const email_modal = document.getElementById("send-device-email-confirm-modal");
    const email_confirm = document.getElementById("send-device-email-confirm-submit");
    if (email_modal && email_confirm)
    {
        email_confirm.addEventListener("click", function () {
            const form = pending_user_list_device_send_form;
            if (!form)
            {
                return;
            }
            pending_user_list_device_send_form = null;
            hide_user_list_device_modal(email_modal);
            send_user_list_device_email(form);
        });
        email_modal.addEventListener("hidden.bs.modal", function () {
            pending_user_list_device_send_form = null;
        });
    }

    const revoke_modal = document.getElementById("user-list-device-revoke-confirm");
    const revoke_confirm = document.getElementById("user-list-device-revoke-confirm-submit");
    if (revoke_modal && revoke_confirm)
    {
        revoke_confirm.addEventListener("click", function () {
            const button = pending_user_list_device_revoke_button;
            if (!button)
            {
                return;
            }
            pending_user_list_device_revoke_button = null;
            hide_user_list_device_modal(revoke_modal);
            revoke_user_list_device(button);
        });
        revoke_modal.addEventListener("hidden.bs.modal", function () {
            pending_user_list_device_revoke_button = null;
        });
    }
}

/**
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function open_user_list_device_email_confirm(button)
{
    if (button.disabled)
    {
        return;
    }
    const form = button.closest(".user-list-device-send-form");
    const modal = document.getElementById("send-device-email-confirm-modal");
    if (!form || !modal || !window.bootstrap || !bootstrap.Modal)
    {
        return;
    }
    pending_user_list_device_send_form = form;
    const confirm_text = modal.querySelector(".send-device-email-confirm-text");
    const username = form.getAttribute("data-username") || "";
    if (confirm_text)
    {
        confirm_text.replaceChildren(
            document.createTextNode("Сигурни ли сте, че искате да изпратите имейл за добавяне на устройство на този потребител: "),
            Object.assign(document.createElement("strong"), { textContent: username }),
            document.createTextNode("?")
        );
    }
    bootstrap.Modal.getOrCreateInstance(modal).show();
}

/**
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function open_user_list_device_revoke_confirm(button)
{
    if (button.disabled)
    {
        return;
    }
    const modal = document.getElementById("user-list-device-revoke-confirm");
    if (!modal || !window.bootstrap || !bootstrap.Modal)
    {
        return;
    }
    pending_user_list_device_revoke_button = button;
    const block = button.closest(".user-list-devices");
    const form = block && block.querySelector(".user-list-device-send-form");
    const username = form ? (form.getAttribute("data-username") || "") : "";
    const device_name = button.getAttribute("data-device-name") || "";
    const confirm_text = modal.querySelector(".device-revoke-confirm-text");
    if (confirm_text)
    {
        confirm_text.replaceChildren(
            document.createTextNode("Сигурни ли сте, че искате да премахнете устройството "),
            Object.assign(document.createElement("strong"), { textContent: device_name }),
            document.createTextNode(" на потребител "),
            Object.assign(document.createElement("strong"), { textContent: username }),
            document.createTextNode("?")
        );
    }
    bootstrap.Modal.getOrCreateInstance(modal).show();
}

/**
 * @param {HTMLElement} modal
 * @returns {void}
 */
function hide_user_list_device_modal(modal)
{
    if (!window.bootstrap || !bootstrap.Modal)
    {
        return;
    }
    const modal_instance = bootstrap.Modal.getInstance(modal) || bootstrap.Modal.getOrCreateInstance(modal);
    modal_instance.hide();
}

/**
 * @param {HTMLButtonElement} button
 * @returns {void}
 */
function revoke_user_list_device(button)
{
    if (button.disabled)
    {
        return;
    }
    button.disabled = true;
    const block = button.closest(".user-list-devices");
    const form = block.querySelector(".user-list-device-send-form");
    const csrf = form.querySelector("[name=csrfmiddlewaretoken]");
    fetch(button.getAttribute("data-revoke-url"), {
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
            load_user_list_devices(block.closest(".user-list-helper-inner"));
            show_user_list_toast("Устройството е премахнато.", "success");
        })
        .catch(function () {
            show_user_list_toast("Устройството не беше премахнато.", "error");
            button.disabled = false;
        });
}
