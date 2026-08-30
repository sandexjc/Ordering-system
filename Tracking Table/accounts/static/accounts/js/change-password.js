/**
 * Initial functions call
 */

/** Minimum required viewport width for change-password page is 600 px */
const MIN_VIEWPORT_WIDTH = 600;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

document.getElementById("change-password-form")?.addEventListener("submit", function () {
    const button = document.getElementById("change-password-submit-btn");
    if (!button || button.disabled) {
        return;
    }
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Изпращане...';
});

