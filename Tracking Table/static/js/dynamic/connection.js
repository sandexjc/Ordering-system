/*
 * dynamic/connection.js
 * ---------------------
 * Server connection status toasts, driven by live-sync heartbeats.
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

document.getElementById("server-connection-toast-retry")?.addEventListener("click", (event) => {
    event.preventDefault();
    if (typeof retryOrdersLiveSync === "function") {
        retryOrdersLiveSync();
    }
});
