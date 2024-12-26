/**
 * Initial functions call
 */

/** Minimum required viewport width is 1000 px */
const MIN_VIEWPORT_WIDTH = 1000;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

/** Set per order required events and callbacks */
handle_orders();