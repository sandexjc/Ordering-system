/**
 * Initial functions call
 */

/** Minimum required viewport width for change-password page is 600 px */
const MIN_VIEWPORT_WIDTH = 600;
/** Current viewport size */
const viewport_width = window.innerWidth;

document.querySelectorAll(".send-password-email-form").forEach(bind_send_password_email_form);

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);
