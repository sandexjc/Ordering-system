/** 
 * Dynamically set content scale based on viewport size and minimum required viewport width
 */

function set_viewport_scale(viewport_width, min_viewport_width)
{
    var meta_scale = document.getElementById("viewport-scale-meta");

    if (viewport_width < min_viewport_width)
    {
        meta_scale.setAttribute("content", "width=device-width, initial-scale=" + viewport_width/min_viewport_width);
    }
}