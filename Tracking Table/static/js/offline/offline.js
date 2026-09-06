/*
 * offline/offline.js
 * ------------------
 * Retry button for the offline fallback page.
 *
 * Loaded from:
 *   - main/templates/components/offline.html
 */

document.getElementById("offline-refresh").addEventListener("click", function () {
    if (this.disabled) {
        return;
    }
    this.disabled = true;
    this.classList.add("is-pending");
    this.setAttribute("aria-busy", "true");
    window.location.reload();
});
