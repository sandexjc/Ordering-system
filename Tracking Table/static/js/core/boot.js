/*
 * core/boot.js
 * ------------
 * Site boot for authenticated pages that use the main layout.
 *
 * Loaded from:
 *   - main/templates/layout/base.html  (end of default scripts block)
 *
 * Depends on (must load first):
 *   - core/viewport.js          → set_viewport_scale
 *   - orders/row-expand/bind-rows.js → handle_orders
 *
 * Side effects on load:
 *   1. Scales viewport when width < 1000px
 *   2. Binds expandable order-row click handlers present at initial render
 */

/** Minimum required viewport width is 1000 px */
const MIN_VIEWPORT_WIDTH = 1000;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

/** Set per order required events and callbacks */
handle_orders();
