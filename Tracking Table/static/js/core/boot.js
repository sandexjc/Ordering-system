/*
 * core/boot.js
 * ------------
 * Site boot for authenticated pages that use the main layout.
 *
 * Loaded from:
 *   - main/templates/layout/base.html  (end of default scripts block)
 *
 * Depends on (must load first):
 *   - orders/row-expand/bind-rows.js → handle_orders
 *
 * Side effects on load:
 *   1. Binds expandable order-row click handlers present at initial render
 *   2. Keeps the orders and vitrine table headers pinned on small screens
 */

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
 */
function pin_order_table_head()
{
    var narrow = window.matchMedia("(max-width: 999px)").matches;

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
 * Buttons, toolbar links, menu items, and sort headers.
 * Row taps and the Разкрой / Витрини tabs already run on their own touch.
 * @param {EventTarget} node
 * @returns {Element|null}
 */
function touch_activate_control(node)
{
    if (!node || !node.closest)
    {
        return null;
    }
    var tag = node.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || tag === "OPTION" || tag === "LABEL")
    {
        return null;
    }
    if (node.closest(".visibleRows, [data-dynamic-view]"))
    {
        return null;
    }
    var el = node.closest("button, a.btn, a.dropdown-item, th[data-sort-by]");
    if (!el || el.disabled || el.classList.contains("disabled") || el.getAttribute("aria-disabled") === "true")
    {
        return null;
    }
    return el;
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
    if (event.pointerType === "mouse" || !event.isPrimary || order_head_gesture_moves)
    {
        return;
    }
    var el = touch_activate_control(event.target);
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
}, { passive: true, capture: true });

document.addEventListener("mousedown", swallow_touch_ghost, true);
document.addEventListener("mouseup", swallow_touch_ghost, true);
document.addEventListener("click", swallow_touch_ghost, true);

place_order_table_head();
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
