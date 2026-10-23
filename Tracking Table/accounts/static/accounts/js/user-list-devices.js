document.querySelectorAll(".user-list-helper-inner").forEach(function (helper_inner) {
    helper_inner.addEventListener("user-list-helper-open", function () {
        load_user_list_devices(helper_inner);
    });
});

document.addEventListener("click", function (event) {
    const button = event.target.closest(".user-list-device-revoke");
    if (!button)
    {
        return;
    }
    revoke_user_list_device(button);
});

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
    const button = form.querySelector("button[type=submit]");
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
