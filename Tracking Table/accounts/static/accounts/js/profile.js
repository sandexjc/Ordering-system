/**
 * Initial functions call
 */

/** Minimum required viewport width for profile page is 600 px */
const MIN_VIEWPORT_WIDTH = 600;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

const profile_devices = document.getElementById("profile-devices");
const profile_device_list = document.getElementById("profile-device-list");
const profile_device_status = document.getElementById("profile-device-status");
const profile_device_send_form = document.getElementById("profile-device-send-form");
if (profile_devices && profile_device_send_form)
{
    load_profile_devices();
    profile_device_send_form.addEventListener("submit", send_profile_device_email);
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
            profile_device_status.textContent = "Устройствата не могат да бъдат заредени.";
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
        profile_device_status.textContent = "Няма добавени устройства.";
        return;
    }
    profile_device_status.textContent = "";
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
 * @param {Event} event
 * @returns {void}
 */
function send_profile_device_email(event)
{
    event.preventDefault();
    const button = document.getElementById("profile-device-send");
    if (!button || button.disabled)
    {
        return;
    }
    button.disabled = true;
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
            if (!response.ok)
            {
                throw new Error("send failed");
            }
            return response.json();
        })
        .then(function (data) {
            profile_device_status.textContent = data && data.ok
                ? "Имейлът за добавяне на устройство е изпратен."
                : "Имейлът не беше изпратен.";
        })
        .catch(function () {
            profile_device_status.textContent = "Имейлът не беше изпратен.";
        })
        .finally(function () {
            button.disabled = false;
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
    button.disabled = true;
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
            load_profile_devices();
        })
        .catch(function () {
            profile_device_status.textContent = "Устройството не беше премахнато.";
            button.disabled = false;
        });
}

