/*
 * offline/register-sw.js
 * ----------------------
 * Register the worker once per browser profile on authenticated pages.
 * updateViaCache "all" allows /sw.js update checks to use HTTP cache
 * (the browser may still make conditional requests for update checks).
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 */

if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistration("/").then(function (registration) {
        if (registration) {
            return;
        }
        return navigator.serviceWorker.register("/sw.js", {
            scope: "/",
            updateViaCache: "all",
        });
    }).catch(function () {});
}
