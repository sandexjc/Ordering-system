/*
 * orders/actions/progress-step.js
 * -------------------------------
 * Click-to-toggle progress steps in expanded dynamic table / vitrine details.
 * Table plate/edge clicks are sequential: activating a step also activates
 * previous ones; deactivating a step also deactivates following ones. Hover
 * previews that. Vitrine only toggles order_ready / order_taken.
 *
 * Loaded from:
 *   - main/templates/dynamic/orders.html
 *
 * Depends on (runtime):
 *   - orders/actions/progress-delete.js → apply_progress_update_response
 *   - orders/details/fetch.js           → cache_order_details
 *   - orders/row-expand/transitions.js  → onHiddenRowContentUpdated
 *
 * Security:
 *   - POST same-origin with X-CSRFToken from the expanded-row {% csrf_token %}
 */

/**
 * CSRF token stored on the expanded order-view container.
 *
 * @param {Element} stepEl - Clicked progress step.
 * @returns {string} CSRF token, or empty string if missing.
 */
function get_progress_step_csrf_token(stepEl)
{
    const orderView = stepEl.closest(".order-view");
    const input = orderView && orderView.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
}

/**
 * Order id from the expanded `#order-view-{id}` wrapper.
 *
 * @param {Element} stepEl - Clicked progress step.
 * @returns {string|null} Order id, or null.
 */
function get_progress_step_order_id(stepEl)
{
    const orderView = stepEl.closest("[id^='order-view-']");
    if (!orderView) {
        return null;
    }
    return orderView.id.replace("order-view-", "");
}

/**
 * Recompute expanded-row height after a step's loading/error UI changes.
 *
 * @param {Element} stepEl - Clicked progress step.
 * @returns {void}
 */
function refresh_progress_step_row_height(stepEl)
{
    const orderId = get_progress_step_order_id(stepEl);
    if (!orderId || typeof onHiddenRowContentUpdated !== "function") {
        return;
    }
    onHiddenRowContentUpdated(document.getElementById("hidden-row-" + orderId));
}

/**
 * All step elements in the same progress bar, including disabled ones.
 *
 * @param {HTMLElement} stepEl - A step in the bar.
 * @returns {HTMLElement[]}
 */
function get_progress_bar_items(stepEl)
{
    const bar = stepEl.closest(".progressbar");
    if (!bar) {
        return [];
    }
    return Array.from(bar.children);
}

/**
 * True when the pointer can hover (skip sticky first-tap preview on touch).
 *
 * @returns {boolean}
 */
function can_hover_progress_preview()
{
    return window.matchMedia && window.matchMedia("(hover: hover)").matches;
}

/**
 * Clear hover preview classes on a progress bar.
 *
 * @param {HTMLElement} stepEl - Any step in the bar.
 * @returns {void}
 */
function clear_progress_step_preview(stepEl)
{
    get_progress_bar_items(stepEl).forEach((item) => {
        item.classList.remove("is-preview", "is-preview-off");
    });
}

/**
 * Preview the sequential result of clicking this step.
 *
 * @param {HTMLElement} stepEl - Hovered progress step.
 * @returns {void}
 */
function preview_progress_step(stepEl)
{
    if (!can_hover_progress_preview()) {
        return;
    }
    if (stepEl.classList.contains("is-loading") || stepEl.classList.contains("is-error")) {
        return;
    }

    const items = get_progress_bar_items(stepEl);
    const index = items.indexOf(stepEl);
    if (index < 0) {
        return;
    }

    const activating = stepEl.dataset.active !== "1";
    items.forEach((item, itemIndex) => {
        item.classList.remove("is-preview", "is-preview-off");
        if (item.classList.contains("disabled") || item.classList.contains("is-loading")) {
            return;
        }
        if (activating && itemIndex <= index && !item.classList.contains("active")) {
            item.classList.add("is-preview");
        }
        if (!activating && itemIndex >= index && item.classList.contains("active")) {
            item.classList.add("is-preview-off");
        }
    });
}

/**
 * Enter the in-step loading state and hide any previous error.
 *
 * @param {HTMLElement} stepEl - Progress step `<li>`.
 * @returns {void}
 */
function set_progress_step_loading(stepEl)
{
    clear_progress_step_preview(stepEl);
    stepEl.classList.add("is-loading");
    stepEl.classList.remove("is-error");
    stepEl.removeAttribute("aria-label");
    stepEl.setAttribute("aria-busy", "true");
}

/**
 * Leave loading; optionally mark the step as failed.
 *
 * @param {HTMLElement} stepEl - Progress step `<li>`.
 * @param {boolean} isError - When true, show the red retry state.
 * @returns {void}
 */
function clear_progress_step_loading(stepEl, isError)
{
    stepEl.classList.remove("is-loading");
    stepEl.removeAttribute("aria-busy");
    stepEl.classList.toggle("is-error", Boolean(isError));
    if (isError) {
        stepEl.setAttribute("aria-label", "Опитай отново");
    } else {
        stepEl.removeAttribute("aria-label");
    }
}

/**
 * POST the intended next boolean for one progress step.
 *
 * @param {HTMLElement} stepEl - Progress step `<li>`.
 * @returns {void}
 */
function submit_progress_step(stepEl)
{
    if (stepEl.classList.contains("is-loading") || stepEl.classList.contains("disabled")) {
        return;
    }

    const url = stepEl.dataset.url;
    const target = stepEl.dataset.itemType;
    const itemId = stepEl.dataset.itemId;
    const field = stepEl.dataset.field;
    const nextValue = stepEl.dataset.active !== "1";
    const csrfToken = get_progress_step_csrf_token(stepEl);

    if (!url || !target || !field || !csrfToken) {
        clear_progress_step_loading(stepEl, true);
        refresh_progress_step_row_height(stepEl);
        return;
    }

    set_progress_step_loading(stepEl);
    refresh_progress_step_row_height(stepEl);

    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({
            target: target,
            item_id: itemId,
            field: field,
            value: nextValue,
        }),
    })
        .then((response) => {
            return response.json().then(
                (data) => ({ ok: response.ok, data: data }),
                () => ({ ok: false, data: {} })
            );
        })
        .then((result) => {
            if (!result.ok) {
                throw new Error((result.data && result.data.error) || "Progress update failed");
            }

            clear_progress_step_loading(stepEl, false);
            if (typeof apply_progress_update_response === "function") {
                apply_progress_update_response(result.data);
            }
            if (typeof rememberLocalOrderMutation === "function") {
                rememberLocalOrderMutation(get_progress_step_order_id(stepEl));
            }

            const orderId = get_progress_step_order_id(stepEl);
            if (orderId && typeof cache_order_details === "function") {
                cache_order_details(orderId);
            }
            refresh_progress_step_row_height(stepEl);
        })
        .catch((error) => {
            console.error(error);
            clear_progress_step_loading(stepEl, true);
            refresh_progress_step_row_height(stepEl);
        });
}

/**
 * True when the event is on the circle hit target (not the full grid cell).
 *
 * @param {Event} event - Mouse event.
 * @returns {boolean}
 */
function is_progress_circle_event(event)
{
    return Boolean(event.target.closest && event.target.closest(".progress-step-hit"));
}

/**
 * Delegated click handler for interactive progress steps on the dynamic page.
 *
 * @param {MouseEvent} event - Document click.
 * @returns {void}
 */
function handle_progress_step_click(event)
{
    const root = document.getElementById("dynamic-orders-root");
    if (!root || !root.contains(event.target)) {
        return;
    }

    const stepEl = event.target.closest("[data-progress-step]");
    if (!stepEl || !root.contains(stepEl)) {
        return;
    }

    if (!event.target.closest(".progress-step-hit")) {
        return;
    }

    event.preventDefault();
    submit_progress_step(stepEl);
}

/**
 * Keyboard activation (Enter / Space) for progress steps.
 *
 * @param {KeyboardEvent} event - Document keydown.
 * @returns {void}
 */
function handle_progress_step_keydown(event)
{
    if (event.key !== "Enter" && event.key !== " ") {
        return;
    }

    const root = document.getElementById("dynamic-orders-root");
    if (!root || !root.contains(event.target)) {
        return;
    }

    const stepEl = event.target.closest("[data-progress-step]");
    if (!stepEl || event.target !== stepEl) {
        return;
    }

    event.preventDefault();
    submit_progress_step(stepEl);
}

/**
 * Delegated hover preview for sequential progress updates.
 *
 * @param {MouseEvent} event - Document mouseover.
 * @returns {void}
 */
function handle_progress_step_mouseover(event)
{
    const root = document.getElementById("dynamic-orders-root");
    if (!root || !root.contains(event.target)) {
        return;
    }

    const stepEl = event.target.closest("[data-progress-step]");
    if (!stepEl || !root.contains(stepEl) || !is_progress_circle_event(event)) {
        return;
    }

    preview_progress_step(stepEl);
}

/**
 * Clear sequential hover preview when leaving a progress bar.
 *
 * @param {MouseEvent} event - Document mouseout.
 * @returns {void}
 */
function handle_progress_step_mouseout(event)
{
    const hit = event.target.closest && event.target.closest(".progress-step-hit");
    if (!hit) {
        return;
    }

    const nextHit = event.relatedTarget && event.relatedTarget.closest
        ? event.relatedTarget.closest(".progress-step-hit")
        : null;
    if (nextHit && nextHit.closest(".progressbar") === hit.closest(".progressbar")) {
        return;
    }

    const stepEl = hit.closest("[data-progress-step]");
    if (stepEl) {
        clear_progress_step_preview(stepEl);
    }
}

if (!window.progressStepClickHandler) {
    window.progressStepClickHandler = handle_progress_step_click;
    window.progressStepKeyHandler = handle_progress_step_keydown;
    window.progressStepMouseOverHandler = handle_progress_step_mouseover;
    window.progressStepMouseOutHandler = handle_progress_step_mouseout;
    document.addEventListener("click", window.progressStepClickHandler);
    document.addEventListener("keydown", window.progressStepKeyHandler);
    document.addEventListener("mouseover", window.progressStepMouseOverHandler);
    document.addEventListener("mouseout", window.progressStepMouseOutHandler);
}
