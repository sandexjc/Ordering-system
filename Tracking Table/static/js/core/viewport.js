/*
 * core/viewport.js
 * ----------------
 * Viewport meta-tag scaling helper for narrow screens.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *   - accounts/templates/accounts/login.html
 *
 * Used by:
 *   - core/boot.js
 *   - accounts/static/accounts/js/login-base.js
 *   - accounts/static/accounts/js/create-user.js
 */

/**
 * Scale the page when the viewport is narrower than the required minimum.
 *
 * @param {number} viewport_width - Current window width in CSS pixels.
 * @param {number} min_viewport_width - Minimum width the layout is designed for.
 * @returns {void}
 */
function set_viewport_scale(viewport_width, min_viewport_width)
{
    var meta_scale = document.getElementById("viewport-scale-meta");

    if (viewport_width < min_viewport_width)
    {
        meta_scale.setAttribute("content", "width=device-width, initial-scale=" + viewport_width/min_viewport_width);
    }
}
