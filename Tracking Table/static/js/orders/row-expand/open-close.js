/*
 * orders/row-expand/open-close.js
 * -------------------------------
 * Open / close animations and focus helpers for expandable order rows.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on (runtime):
 *   - orders/row-expand/transitions.js → _cancelPendingTransitionAndLockHeight, _onRowHeightTransitionEnd
 *   - orders/details/fetch.js          → get_order
 *   - orders/details/spinner.js        → set_hidden_row_close_visible
 *
 * Used by:
 *   - orders/row-expand/bind-rows.js
 *   - js/dynamic/cache.js (restoreOpenRows)
 */

/**
 * After folding via the close button, scroll the order row into view and focus it.
 *
 * @param {HTMLElement|null} visibleRow - The `.visibleRows` tr to focus.
 * @returns {void}
 */
function focusClosedOrderRow(visibleRow) {
  if (!visibleRow) {
    return;
  }

  if (!visibleRow.hasAttribute("tabindex")) {
    visibleRow.setAttribute("tabindex", "-1");
  }

  visibleRow.scrollIntoView({ block: "center", behavior: "smooth", inline: "nearest" });
  requestAnimationFrame(() => {
    visibleRow.focus({ preventScroll: true });
  });
}

/**
 * Smooth-expand a hidden detail row, mark selection, and fetch details on first open.
 *
 * @param {HTMLElement} hiddenRow - The `#hidden-row-{id}` element.
 * @param {string} row_id - Order / vitrine id (also the visible row element id).
 * @param {HTMLElement|null} visibleRow - The clicked `.visibleRows` tr, if any.
 * @returns {void}
 */
function openHiddenRow(hiddenRow, row_id, visibleRow) {

  // cancel any pending transition handlers and lock current height (if any)
  _cancelPendingTransitionAndLockHeight(hiddenRow);

  // mark not-closing
  hiddenRow.classList.remove("is-closing");
  hiddenRow._isClosing = false;

  // ensure visible to measure
  hiddenRow.style.display = "block";

  // Start from zero so the expand animation runs
  // But if height is currently a px value (from lock), keep it as start, else set to 0
  const startHeight = hiddenRow.style.height;
  // If currently not 0 (e.g., we locked to some px), we start from that; otherwise zero
  if (!startHeight || startHeight === "0px") {
    hiddenRow.style.height = "0px";
  } else {
    hiddenRow.style.height = startHeight;
  }

  // Force reflow so the start height is applied
  hiddenRow.getBoundingClientRect();

  // Target height is the scrollHeight (content height)
  const targetHeight = hiddenRow.scrollHeight + "px";

  hiddenRow._isAnimating = true;
  _onRowHeightTransitionEnd(hiddenRow, function () {
    hiddenRow.style.height = "auto";
    hiddenRow._isAnimating = false;
    hiddenRow.classList.add("is-open");
  });

  // trigger animation to target height
  requestAnimationFrame(() => {
    hiddenRow.style.height = targetHeight;
  });

  // visual classes & focus & fetch logic (identical to original)
  hiddenRow.classList.add("orderClicked");
  if (visibleRow) visibleRow.classList.add("rowSelected");
  hiddenRow.focus();

  if (!hiddenRow.classList.contains("fetch-prevent")) {
    hiddenRow.classList.add("fetch-prevent");
    get_order(row_id);
  } else if (typeof set_hidden_row_close_visible === "function") {
    /** Content already loaded (cache / prior fetch) — keep fold button available. */
    set_hidden_row_close_visible(row_id, true);
  }

  hiddenRow._isOpen = true;
  if (typeof syncOpenRowId === "function") {
    syncOpenRowId(row_id, true);
  }
}

/**
 * Smooth-collapse a hidden detail row and clear selection classes.
 *
 * @param {HTMLElement} hiddenRow - The `#hidden-row-{id}` element.
 * @param {HTMLElement|null} visibleRow - The related `.visibleRows` tr, if any.
 * @returns {void}
 */
function closeHiddenRow(hiddenRow, visibleRow) {

  // Cancel prior handlers and lock current visual height (so transition starts from visible height)
  _cancelPendingTransitionAndLockHeight(hiddenRow);

  hiddenRow.classList.add("is-closing");
  hiddenRow._isClosing = true;

  // If height is 'auto' or blank, set it to the measured px so the transition can animate from there
  if (hiddenRow.style.height === "" || hiddenRow.style.height === "auto") {
    hiddenRow.style.height = hiddenRow.scrollHeight + "px";
  }

  // Force layout so the locked height applies
  hiddenRow.getBoundingClientRect();

  hiddenRow._isAnimating = true;
  _onRowHeightTransitionEnd(hiddenRow, function () {
    hiddenRow.style.display = "none";
    hiddenRow.style.height = "0px";
    hiddenRow.classList.remove("is-closing");
    hiddenRow._isClosing = false;
    hiddenRow._isAnimating = false;
    hiddenRow.classList.remove("is-open");
  });

  // trigger collapse on next frame
  requestAnimationFrame(() => {
    hiddenRow.style.height = "0px";
  });

  hiddenRow.classList.remove("orderClicked");
  if (visibleRow) visibleRow.classList.remove("rowSelected");

  hiddenRow._isOpen = false;
  if (typeof syncOpenRowId === "function") {
    const rowId = hiddenRow.id.replace("hidden-row-", "");
    syncOpenRowId(rowId, false);
  }
}
