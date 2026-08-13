/*
 * orders/row-expand/transitions.js
 * --------------------------------
 * Height-transition helpers for expandable order detail rows.
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Used by:
 *   - orders/row-expand/open-close.js
 *   - orders/details/fetch.js
 */

/**
 * Cancel any pending height transitionend handler and lock the row to its
 * current computed pixel height so the next animation starts from the visible size.
 *
 * @param {HTMLElement} hiddenRow - The `.hiddenRows` element being animated.
 * @returns {void}
 */
function _cancelPendingTransitionAndLockHeight(hiddenRow) {
  // remove any stored transition handler
  if (hiddenRow._pendingTransitionHandler) {
    hiddenRow.removeEventListener("transitionend", hiddenRow._pendingTransitionHandler);
    hiddenRow._pendingTransitionHandler = null;
  }

  // compute current computed height (px)
  const cs = window.getComputedStyle(hiddenRow);
  // If it's not displayed, leave (no locking needed)
  if (cs.display === "none") return;

  // convert computed height to px and lock as inline height so animations start from current visual height
  hiddenRow.style.height = hiddenRow.getBoundingClientRect().height + "px";
}

/**
 * After async content is inserted into an open hidden row, re-animate height
 * from the current size to the new scrollHeight. No-op if the row is closing or hidden.
 *
 * @param {HTMLElement|null} hiddenRow - The `.hiddenRows` element whose content changed.
 * @returns {void}
 */
function onHiddenRowContentUpdated(hiddenRow) {

  // skip if node missing
  if (!hiddenRow) return;

  // Ignore updates while row is closing
  if (hiddenRow.classList.contains("is-closing") || hiddenRow._isClosing) return;

  const cs = window.getComputedStyle(hiddenRow);
  if (cs.display === "none" || cs.height === "0px") return;

  // If an animation is currently pending, lock current computed height and proceed
  _cancelPendingTransitionAndLockHeight(hiddenRow);

  // Lock current height (visual)
  const currentHeight = hiddenRow.scrollHeight;
  hiddenRow.style.height = currentHeight + "px";

  // Force reflow
  hiddenRow.getBoundingClientRect();

  // compute new height after content inserted
  const newHeight = hiddenRow.scrollHeight;

  // attach a once transitionend handler to reset to auto
  const updateHandler = function (e) {
    if (e.target !== hiddenRow || e.propertyName !== "height") return;
    hiddenRow.style.height = "auto";
    hiddenRow._isAnimating = false;
    hiddenRow._pendingTransitionHandler = null;
  };

  hiddenRow._pendingTransitionHandler = updateHandler;
  hiddenRow._isAnimating = true;
  hiddenRow.addEventListener("transitionend", updateHandler, { once: true });

  // animate to new height
  requestAnimationFrame(() => {
    hiddenRow.style.height = newHeight + "px";
  });
}
