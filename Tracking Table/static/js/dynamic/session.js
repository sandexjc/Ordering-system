/*
 * dynamic/session.js
 * ------------------
 * Detect expired Django sessions on XHR/fetch and send the tab to login.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html (after state.js)
 *
 * Runtime depends on:
 *   - dynamic/sync.js → pauseOrdersLiveSync (optional)
 */

/**
 * Login URL that returns the user to the current dynamic page after auth.
 *
 * @returns {string}
 */
function buildLoginUrl()
{
    const next = window.location.pathname + window.location.search;
    return "/accounts/login/?next=" + encodeURIComponent(next);
}

/**
 * True when a URL is the accounts login page.
 *
 * @param {string} url - Absolute or relative URL.
 * @returns {boolean}
 */
function isLoginUrl(url)
{
    if (!url) {
        return false;
    }
    try {
        const path = new URL(url, window.location.origin).pathname.replace(/\/+$/, "");
        return path === "/accounts/login";
    } catch (error) {
        return String(url).indexOf("/accounts/login") !== -1;
    }
}

/**
 * If this response means the session is gone, navigate to login.
 *
 * @param {Response} response - fetch() response.
 * @returns {boolean} True when a redirect was started.
 */
function redirectToLoginIfUnauthenticated(response)
{
    if (!response) {
        return false;
    }
    const sessionExpired = response.status === 401
        || (response.redirected && isLoginUrl(response.url));
    if (!sessionExpired) {
        return false;
    }
    if (typeof pauseOrdersLiveSync === "function") {
        pauseOrdersLiveSync();
    }
    window.location.replace(buildLoginUrl());
    return true;
}
