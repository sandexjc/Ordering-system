/*
 * dynamic/connection.js
 * ---------------------
 * Server connection status toasts, driven by live-sync heartbeats.
 * Also the toast shown when another user deletes an order on the open board.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html (after state.js, before sync.js)
 *
 * Runtime depends on:
 *   - dynamic/sync.js → retryOrdersLiveSync
 */

let serverConnectionToastInstance = null;
let serverConnectionRestoredToastInstance = null;
let serverConnectionCountdownTimer = null;
let remoteDeletedOrderNotices = [];
let remoteDeletedOrderToastTimer = null;
let remoteDeletedOrderToastBound = false;

const REMOTE_DELETED_ORDER_TOAST_MS = 12000;

/**
 * Bootstrap Toast instance, created once per element.
 *
 * @param {string} elementId - Toast root id.
 * @param {object|null} cachedInstance - Previously created instance.
 * @param {object} options - bootstrap.Toast options.
 * @returns {object|null}
 */
function getBootstrapToast(elementId, cachedInstance, options)
{
    if (cachedInstance) {
        return cachedInstance;
    }
    const toastEl = document.getElementById(elementId);
    if (!toastEl || typeof bootstrap === "undefined" || !bootstrap.Toast) {
        return null;
    }
    return bootstrap.Toast.getOrCreateInstance(toastEl, options);
}

/**
 * Offline toast instance (stays until reconnect).
 *
 * @returns {object|null}
 */
function getServerConnectionToast()
{
    if (!serverConnectionToastInstance) {
        const toastEl = document.getElementById("server-connection-toast");
        serverConnectionToastInstance = getBootstrapToast(
            "server-connection-toast",
            null,
            { autohide: false }
        );
        if (toastEl && serverConnectionToastInstance) {
            toastEl.addEventListener("hidden.bs.toast", () => {
                stopServerConnectionCountdown();
            });
        }
    }
    return serverConnectionToastInstance;
}

/**
 * Restored toast instance (auto-hides after a few seconds).
 *
 * @returns {object|null}
 */
function getServerConnectionRestoredToast()
{
    if (!serverConnectionRestoredToastInstance) {
        serverConnectionRestoredToastInstance = getBootstrapToast(
            "server-connection-restored-toast",
            null,
            { autohide: true, delay: 8000 }
        );
    }
    return serverConnectionRestoredToastInstance;
}

/**
 * Seconds remaining until the next scheduled heartbeat.
 *
 * @returns {number}
 */
function getSecondsUntilNextHeartbeat()
{
    const remainingMs = Math.max(0, (ordersSyncNextTickAt || 0) - Date.now());
    return Math.ceil(remainingMs / 1000);
}

/**
 * Refresh countdown labels on the offline toast.
 *
 * @returns {void}
 */
function refreshServerConnectionToast()
{
    const countdownEl = document.getElementById("server-connection-toast-countdown");
    if (countdownEl) {
        countdownEl.textContent = String(getSecondsUntilNextHeartbeat());
    }
}

/**
 * Stop the 1s countdown interval.
 *
 * @returns {void}
 */
function stopServerConnectionCountdown()
{
    if (serverConnectionCountdownTimer) {
        window.clearInterval(serverConnectionCountdownTimer);
        serverConnectionCountdownTimer = null;
    }
}

/**
 * Keep the toast countdown in sync with the next heartbeat.
 *
 * @returns {void}
 */
function startServerConnectionCountdown()
{
    stopServerConnectionCountdown();
    refreshServerConnectionToast();
    serverConnectionCountdownTimer = window.setInterval(refreshServerConnectionToast, 250);
}

/**
 * Switch the offline toast between countdown and in-flight spinner.
 *
 * @param {boolean} isPending - True while a reconnect request is waiting for a response.
 * @returns {void}
 */
function setServerConnectionToastPending(isPending)
{
    const toastEl = document.getElementById("server-connection-toast");
    if (!toastEl) {
        return;
    }
    toastEl.classList.toggle("is-awaiting-response", Boolean(isPending));
    const retryBtn = document.getElementById("server-connection-toast-retry");
    if (retryBtn) {
        retryBtn.disabled = Boolean(isPending);
    }
    if (isPending) {
        stopServerConnectionCountdown();
        return;
    }
    if (!isServerConnected) {
        startServerConnectionCountdown();
    }
}

/**
 * Hide a toast if the instance exists.
 *
 * @param {object|null} toast - bootstrap.Toast instance.
 * @returns {void}
 */
function hideToast(toast)
{
    if (toast) {
        toast.hide();
    }
}

/**
 * Hide the offline toast without changing connection state.
 *
 * @returns {void}
 */
function hideServerConnectionToast()
{
    stopServerConnectionCountdown();
    const toastEl = document.getElementById("server-connection-toast");
    if (toastEl) {
        toastEl.classList.remove("is-awaiting-response");
    }
    hideToast(getServerConnectionToast());
}

/**
 * Record heartbeat success/failure and show the matching toast.
 *
 * @param {boolean} isConnected - True when the last poll got a successful response.
 * @returns {void}
 */
function setServerConnected(isConnected)
{
    const wasConnected = isServerConnected;
    isServerConnected = Boolean(isConnected);
    if (isServerConnected) {
        hideServerConnectionToast();
        if (!wasConnected) {
            const restoredToast = getServerConnectionRestoredToast();
            if (restoredToast) {
                restoredToast.show();
            }
        }
        return;
    }
    hideToast(getServerConnectionRestoredToast());
    const toast = getServerConnectionToast();
    if (toast) {
        toast.show();
    }
    setServerConnectionToastPending(false);
}

/**
 * One-line notice for a single deleted order.
 *
 * @param {{id: string, owner: string}} entry - Order number and owner.
 * @returns {string}
 */
function remoteDeletedOrderSentence(entry)
{
    let sentence = "Поръчка";
    if (entry.id) {
        sentence += " №" + entry.id;
    }
    if (entry.owner) {
        sentence += " на " + entry.owner;
    }
    return sentence + " беше изтрита от друг потребител.";
}

/**
 * One list line when several orders were deleted together.
 *
 * @param {{id: string, owner: string}} entry - Order number and owner.
 * @returns {string}
 */
function remoteDeletedOrderLine(entry)
{
    if (entry.id && entry.owner) {
        return "№" + entry.id + " — " + entry.owner;
    }
    if (entry.id) {
        return "№" + entry.id;
    }
    return entry.owner || "Поръчка";
}

/**
 * Fill the delete toast from the notices collected since it was last closed.
 *
 * @returns {void}
 */
function renderRemoteDeletedOrdersToast()
{
    const titleEl = document.getElementById("remote-order-deleted-toast-title");
    const bodyEl = document.getElementById("remote-order-deleted-toast-body");
    const entries = remoteDeletedOrderNotices;
    if (titleEl) {
        titleEl.textContent = entries.length > 1 ? "Поръчките са изтрити" : "Поръчката е изтрита";
    }
    if (!bodyEl) {
        return;
    }
    bodyEl.replaceChildren();
    if (entries.length <= 1) {
        bodyEl.textContent = entries.length ? remoteDeletedOrderSentence(entries[0]) : "";
        return;
    }
    const list = document.createElement("ul");
    list.className = "remote-order-deleted-toast-list";
    entries.forEach((entry) => {
        const item = document.createElement("li");
        item.textContent = remoteDeletedOrderLine(entry);
        list.appendChild(item);
    });
    const note = document.createElement("p");
    note.className = "remote-order-deleted-toast-note";
    note.textContent = "Изтрити са от друг потребител.";
    bodyEl.append(list, note);
}

/**
 * Clear the notice list once the toast has finished hiding.
 *
 * @returns {void}
 */
function bindRemoteDeletedOrderToast()
{
    if (remoteDeletedOrderToastBound) {
        return;
    }
    const toastEl = document.getElementById("remote-order-deleted-toast");
    if (!toastEl) {
        return;
    }
    remoteDeletedOrderToastBound = true;
    toastEl.addEventListener("hidden.bs.toast", () => {
        window.clearTimeout(remoteDeletedOrderToastTimer);
        remoteDeletedOrderToastTimer = null;
        remoteDeletedOrderNotices = [];
    });
}

/**
 * Tell the user that another person deleted one or more orders on this board.
 *
 * Later deletes in the same sitting are added to the open toast.
 *
 * @param {Array<{id: string, owner: string}>} entries - Orders removed from the live board.
 * @returns {void}
 */
function showRemoteDeletedOrdersToast(entries)
{
    const incoming = Array.isArray(entries) ? entries.filter(Boolean) : [];
    if (!incoming.length) {
        return;
    }
    const toastEl = document.getElementById("remote-order-deleted-toast");
    if (!toastEl || typeof bootstrap === "undefined" || !bootstrap.Toast) {
        return;
    }
    bindRemoteDeletedOrderToast();
    incoming.forEach((entry) => {
        const id = entry.id != null ? String(entry.id) : "";
        const owner = entry.owner ? String(entry.owner) : "";
        const duplicate = id !== "" && remoteDeletedOrderNotices.some((item) => item.id === id);
        if (!duplicate) {
            remoteDeletedOrderNotices.push({ id: id, owner: owner });
        }
    });
    renderRemoteDeletedOrdersToast();
    const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { autohide: false });
    toast.show();
    window.clearTimeout(remoteDeletedOrderToastTimer);
    remoteDeletedOrderToastTimer = window.setTimeout(() => {
        toast.hide();
    }, REMOTE_DELETED_ORDER_TOAST_MS);
}

document.getElementById("server-connection-toast-retry")?.addEventListener("click", (event) => {
    event.preventDefault();
    if (typeof retryOrdersLiveSync === "function") {
        retryOrdersLiveSync();
    }
});
