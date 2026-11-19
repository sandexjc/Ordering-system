/*
 * core/boot.js
 * ------------
 * Site boot for authenticated pages that use the main layout.
 *
 * Loaded from:
 *   - main/templates/layout/base.html  (end of default scripts block)
 *
 * Depends on (must load first):
 *   - core/viewport.js          → set_viewport_scale, responsive_viewport_scale
 *   - orders/row-expand/bind-rows.js → handle_orders
 *
 * Side effects on load:
 *   1. Legacy scale: shrink the page when width < 1000px
 *      Responsive scale: leave that shrink off and pin narrow table headers
 *   2. Binds expandable order-row click handlers present at initial render
 *   3. Replays a phone tap as one click. This does not depend on the scale mode.
 */

/** Minimum required viewport width is 1000 px */
const MIN_VIEWPORT_WIDTH = 1000;
/** Current viewport size */
const viewport_width = window.innerWidth;

/** Set viewport scale based on min required viewport width and current viewport width */
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

/** Set per order required events and callbacks */
handle_orders();

/** Orders and vitrine list tables. */
function order_list_tables()
{
    return document.querySelectorAll(".table-scroll > table.table, #dynamic-orders-table-container > table.table");
}

/** Remember the first header row height so the second row sticks beneath it. */
function place_order_table_head()
{
    order_list_tables().forEach(function (table)
    {
        var head = table.tHead;
        if (!head || !head.rows.length)
        {
            return;
        }
        table.style.setProperty("--order-head-row", head.rows[0].offsetHeight + "px");
    });
}

/**
 * On a narrow screen the table scroller blocks normal sticky headers.
 * Slide the header down with the page, and sideways with the columns.
 * Pinned cells do not take hits. A tap on that paint is claimed below,
 * so it can sort instead of opening the order row underneath.
 */
function pin_order_table_head()
{
    var narrow = responsive_viewport_scale()
        && window.matchMedia("(max-width: 999px)").matches;

    order_list_tables().forEach(function (table)
    {
        var head = table.tHead;
        if (!head)
        {
            return;
        }

        var pin = 0;
        if (narrow)
        {
            var table_top = table.getBoundingClientRect().top;
            if (table_top < -8)
            {
                var limit = table.offsetHeight - head.offsetHeight;
                pin = Math.min(-table_top, Math.max(0, limit));
            }
        }

        var transform = pin ? "translateY(" + pin + "px)" : "";
        var position = pin ? "relative" : "";
        var pointer_events = pin ? "none" : "";
        Array.prototype.forEach.call(head.rows, function (row)
        {
            Array.prototype.forEach.call(row.cells, function (cell)
            {
                if (cell.style.transform !== transform)
                {
                    cell.style.transform = transform;
                }
                if (cell.style.position !== position)
                {
                    cell.style.position = position;
                }
                if (cell.style.pointerEvents !== pointer_events)
                {
                    cell.style.pointerEvents = pointer_events;
                }
            });
        });
    });
}

var order_head_pin_frame = 0;
var order_head_hold_pin = false;
var order_head_touch_x = 0;
var order_head_touch_y = 0;
var order_head_gesture_moves = false;
/** Header cell under the finger when the pinned header was touched. */
var order_head_touch_cell = null;
/** A thumb tap often slides a few pixels. Past this, the gesture is a scroll. */
var order_head_touch_slop = 24;
var touch_finger_down = false;
var touch_gesture_activated = false;
var touch_activate_until = 0;
var touch_activate_synthetic = false;

/**
 * A tap must not move the header. Moving it between touch and click
 * makes the phone drop that tap for every button on the page.
 */
function hold_order_table_head()
{
    order_head_hold_pin = true;
    if (order_head_pin_frame)
    {
        window.cancelAnimationFrame(order_head_pin_frame);
        order_head_pin_frame = 0;
    }
}

function schedule_order_table_head()
{
    if (order_head_hold_pin || order_head_pin_frame)
    {
        return;
    }
    order_head_pin_frame = window.requestAnimationFrame(function ()
    {
        order_head_pin_frame = 0;
        if (order_head_hold_pin)
        {
            return;
        }
        pin_order_table_head();
    });
}

/**
 * Controls that run on click.
 * A phone often uses the first tap for :hover and never sends the click,
 * so the finger-up runs that click once. The follow-up click is swallowed.
 * Row taps and the Разкрой / Витрини tabs already run on their own touch.
 * @param {EventTarget} node
 * @returns {Element|null}
 */
function touch_activate_control(node)
{
    if (!node)
    {
        return null;
    }
    if (node.nodeType !== 1)
    {
        node = node.parentElement;
    }
    if (!node || !node.closest)
    {
        return null;
    }
    var tag = node.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || tag === "OPTION" || tag === "LABEL")
    {
        return null;
    }
    if (node.closest(".visibleRows, [data-dynamic-view], [data-progress-step]"))
    {
        return null;
    }
    var el = node.closest("button, summary, a[href], [data-bs-toggle], th[data-sort-by]");
    if (!el || el.disabled || el.classList.contains("disabled") || el.getAttribute("aria-disabled") === "true")
    {
        return null;
    }
    if (control_focuses_text_field(el))
    {
        return null;
    }
    return el;
}

/**
 * A replayed click cannot raise the phone keyboard.
 * Buttons that open a text field focus it from their own touch.
 * @param {Element} el
 * @returns {boolean}
 */
function control_focuses_text_field(el)
{
    var id = el.getAttribute("aria-controls");
    var field = id ? document.getElementById(id) : null;
    return !!(field && (field.tagName === "INPUT" || field.tagName === "TEXTAREA"));
}

/**
 * Header cell painted over this point while the mobile header is pinned.
 * @param {number} x
 * @param {number} y
 * @returns {HTMLTableCellElement|null}
 */
function pinned_order_head_cell_at(x, y)
{
    var found = null;
    order_list_tables().forEach(function (table)
    {
        var head = table.tHead;
        if (!head || found)
        {
            return;
        }
        var table_hit = null;
        Array.prototype.forEach.call(head.rows, function (row)
        {
            Array.prototype.forEach.call(row.cells, function (cell)
            {
                var transform = cell.style.transform;
                if (!transform || transform === "none")
                {
                    return;
                }
                var rect = cell.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0)
                {
                    return;
                }
                if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom)
                {
                    table_hit = cell;
                }
            });
        });
        if (table_hit)
        {
            found = table_hit;
        }
    });
    return found;
}

/**
 * True when the touch landed in the table under the painted header.
 * A menu or dialog above the table keeps its own tap.
 * @param {Event} event
 * @param {Element} cell
 * @returns {boolean}
 */
function tap_is_under_pinned_header(event, cell)
{
    var table = cell.closest("table");
    var target = event.target;
    return !!(table && target && table.contains(target));
}

/**
 * A phone tap often never produces the click that closes a Bootstrap menu
 * and drops focus from its button. Do that for every open menu.
 * The toggle itself is left alone so its own tap can open or close it.
 * @param {EventTarget} target
 * @returns {void}
 */
function settle_touch_menus(target)
{
    var node = target && target.nodeType === 1 ? target : (target && target.parentElement);
    if (!node || !node.closest || typeof bootstrap === "undefined" || !bootstrap.Dropdown)
    {
        return;
    }
    if (node.closest("[data-bs-toggle='dropdown']"))
    {
        return;
    }
    var toggles = document.querySelectorAll(".dropdown-toggle.show");
    Array.prototype.forEach.call(toggles, function (toggle)
    {
        bootstrap.Dropdown.getOrCreateInstance(toggle).hide();
        if (document.activeElement === toggle)
        {
            toggle.blur();
        }
    });
}

/**
 * Keep a pinned-header tap from opening the order row underneath.
 * @param {Event} event
 * @returns {void}
 */
function claim_pinned_header_tap(event)
{
    touch_gesture_activated = true;
    touch_activate_until = Date.now() + 700;
    event.preventDefault();
    event.stopImmediatePropagation();
}

/** The phone sends a second click after the touch. That click must not run the control again. */
function swallow_touch_ghost(event)
{
    if (touch_activate_synthetic || !event.isTrusted)
    {
        return;
    }
    if (!touch_gesture_activated || touch_finger_down || Date.now() > touch_activate_until)
    {
        return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
}

document.addEventListener("pointerdown", function (event)
{
    if (event.pointerType === "mouse")
    {
        return;
    }
    order_head_gesture_moves = false;
    if (event.isPrimary)
    {
        order_head_touch_cell = pinned_order_head_cell_at(event.clientX, event.clientY);
    }
    hold_order_table_head();
}, { capture: true });

document.addEventListener("touchstart", function (event)
{
    touch_finger_down = true;
    touch_gesture_activated = false;
    order_head_gesture_moves = false;
    hold_order_table_head();
    if (event.touches && event.touches[0])
    {
        order_head_touch_x = event.touches[0].clientX;
        order_head_touch_y = event.touches[0].clientY;
        order_head_touch_cell = pinned_order_head_cell_at(order_head_touch_x, order_head_touch_y);
    }
}, { passive: true, capture: true });

document.addEventListener("touchmove", function (event)
{
    if (!event.touches || !event.touches[0] || order_head_gesture_moves)
    {
        return;
    }
    var dx = Math.abs(event.touches[0].clientX - order_head_touch_x);
    var dy = Math.abs(event.touches[0].clientY - order_head_touch_y);
    if (dx > order_head_touch_slop || dy > order_head_touch_slop)
    {
        order_head_gesture_moves = true;
        order_head_hold_pin = false;
        schedule_order_table_head();
    }
}, { passive: true, capture: true });

document.addEventListener("pointerup", function (event)
{
    if (event.pointerType === "mouse" || !event.isPrimary)
    {
        return;
    }
    var pinned = order_head_touch_cell;
    order_head_touch_cell = null;
    var header_tap = pinned && tap_is_under_pinned_header(event, pinned);
    if (header_tap)
    {
        claim_pinned_header_tap(event);
    }
    if (order_head_gesture_moves)
    {
        return;
    }
    settle_touch_menus(event.target);
    var el = header_tap ? touch_activate_control(pinned) : touch_activate_control(event.target);
    if (!el)
    {
        return;
    }
    touch_gesture_activated = true;
    touch_activate_until = Date.now() + 700;
    touch_activate_synthetic = true;
    try
    {
        el.click();
    }
    finally
    {
        touch_activate_synthetic = false;
    }
}, true);

document.addEventListener("touchend", function (event)
{
    touch_finger_down = false;
    if (order_head_gesture_moves)
    {
        if (touch_gesture_activated && event.cancelable)
        {
            event.preventDefault();
        }
        order_head_hold_pin = false;
        schedule_order_table_head();
        return;
    }
    if (touch_gesture_activated && event.cancelable)
    {
        event.preventDefault();
    }
    window.setTimeout(function ()
    {
        order_head_hold_pin = false;
        schedule_order_table_head();
    }, 700);
}, { passive: false, capture: true });

document.addEventListener("touchcancel", function ()
{
    touch_finger_down = false;
    order_head_hold_pin = false;
    order_head_touch_cell = null;
}, { passive: true, capture: true });

document.addEventListener("mousedown", swallow_touch_ghost, true);
document.addEventListener("mouseup", swallow_touch_ghost, true);
document.addEventListener("click", swallow_touch_ghost, true);

place_order_table_head();
if (responsive_viewport_scale())
{
    pin_order_table_head();
    window.addEventListener("scroll", schedule_order_table_head, { passive: true });
    window.addEventListener("resize", function ()
    {
        place_order_table_head();
        schedule_order_table_head();
    });

    var order_table_container = document.getElementById("dynamic-orders-table-container");
    if (order_table_container && window.MutationObserver)
    {
        new MutationObserver(function ()
        {
            place_order_table_head();
            schedule_order_table_head();
        }).observe(order_table_container, { childList: true });
    }
}
else
{
    window.addEventListener("resize", place_order_table_head);
}

/* Text size and row density change header height without a window resize. */
if (window.MutationObserver)
{
    new MutationObserver(function ()
    {
        place_order_table_head();
        if (responsive_viewport_scale())
        {
            schedule_order_table_head();
        }
    }).observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-text", "data-density"]
    });
}
