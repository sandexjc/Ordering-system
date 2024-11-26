/** 
 * Dynamically set content scale based on viewport size 
 */
function set_viewport_scale()
{
    const viewport_width = window.innerWidth;
    var meta_scale = document.getElementById("viewport-scale-meta");

    if (viewport_width < 1000)
    {
        meta_scale.setAttribute("content", "width=device-width, initial-scale=" + viewport_width/1000);
    }

}

set_viewport_scale();