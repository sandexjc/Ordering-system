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
 * Run `handler` only for this row's own height transition (ignore bubbled
 * child transitions such as the fold button hover).
 *
 * @param {HTMLElement} hiddenRow - The `.hiddenRows` element being animated.
 * @param {function(TransitionEvent): void} handler - Called once on height end.
 * @returns {function(TransitionEvent): void} Listener stored on the row.
 */
function _onRowHeightTransitionEnd(hiddenRow, handler)
{
  const wrapped = function (e) {
    if (e.target !== hiddenRow || e.propertyName !== "height") {
      return;
    }
    hiddenRow.removeEventListener("transitionend", wrapped);
    if (hiddenRow._pendingTransitionHandler === wrapped) {
      hiddenRow._pendingTransitionHandler = null;
    }
    handler(e);
  };
  hiddenRow._pendingTransitionHandler = wrapped;
  hiddenRow.addEventListener("transitionend", wrapped);
  return wrapped;
}

/**
 * After async content is inserted into an open hidden row, re-animate height
 * from the current visual size to the new content height. No-op if the row is
 * closing or hidden. Measures with height:auto so a locked (reload) size can
 * shrink as well as grow.
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

  const currentHeight = hiddenRow.getBoundingClientRect().height;

  // scrollHeight on a locked px height reports the lock, not shorter content
  hiddenRow.style.transition = "none";
  hiddenRow.style.height = "auto";
  const newHeight = hiddenRow.scrollHeight;
  hiddenRow.style.height = currentHeight + "px";
  hiddenRow.getBoundingClientRect();
  hiddenRow.style.transition = "";

  if (Math.abs(currentHeight - newHeight) < 1) {
    hiddenRow.style.height = "auto";
    hiddenRow._isAnimating = false;
    return;
  }

  hiddenRow.getBoundingClientRect();

  hiddenRow._isAnimating = true;
  _onRowHeightTransitionEnd(hiddenRow, function () {
    hiddenRow.style.height = "auto";
    hiddenRow._isAnimating = false;
  });

  // animate to new height
  requestAnimationFrame(() => {
    hiddenRow.style.height = newHeight + "px";
  });
}
