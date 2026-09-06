/*
 * offline/register-sw.js
 * ----------------------
 * Register the site-root service worker after a successful page load.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * The worker is served from /sw.js so its scope covers all app URLs.
 */

if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(function () {});
}
