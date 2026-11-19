/**
 * Initial functions call
 */

/** Minimum required viewport width for login, set-password, and device activation is 500 px */
const MIN_VIEWPORT_WIDTH = 500;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);
