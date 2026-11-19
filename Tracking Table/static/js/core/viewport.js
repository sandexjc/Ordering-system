/*
 * core/viewport.js
 * ----------------
 * Chooses between the two narrow-screen scaling modes.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *   - accounts/templates/accounts/login.html
 *   - accounts/templates/accounts/activate-device.html
 *   - accounts/templates/accounts/set-password.html
 *
 * Used by:
 *   - core/boot.js
 *   - accounts/static/accounts/js/login-base.js
 *   - accounts/static/accounts/js/create-user.js
 *   - accounts/static/accounts/js/profile.js
 *   - accounts/static/accounts/js/user-list.js
 *   - accounts/static/accounts/js/change-password.js
 *   - vitrine/static/vitrine/js/price_settings.js
 *
 * The mode comes from DJANGO_FEATURES__RESPONSIVE_SCALE, printed on <html>
 * as data-viewport-scale="responsive" or data-viewport-scale="legacy".
 */

/**
 * Current scaling keeps the page at normal size. Wide tables scroll.
 * @returns {boolean}
 */
function responsive_viewport_scale()
{
    return document.documentElement.getAttribute("data-viewport-scale") === "responsive";
}

/**
 * Previous scaling. Shrink the page when the viewport is narrower than
 * the minimum the layout was built for.
 *
 * No-op while responsive scaling is on.
 *
 * @param {number} viewport_width - Current window width in CSS pixels.
 * @param {number} min_viewport_width - Minimum width the layout is designed for.
 * @returns {void}
 */
function set_viewport_scale(viewport_width, min_viewport_width)
{
    if (responsive_viewport_scale())
    {
        return;
    }

    var meta_scale = document.getElementById("viewport-scale-meta");
    if (!meta_scale || viewport_width >= min_viewport_width)
    {
        return;
    }

    meta_scale.setAttribute(
        "content",
        "width=device-width, initial-scale=" + viewport_width / min_viewport_width
    );
}
