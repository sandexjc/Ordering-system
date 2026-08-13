/*
 * orders/row-expand/bind-rows.js
 * ------------------------------
 * Bind click handlers on visible order rows (once per element via WeakSet).
 *
 * Loaded from:
 *   - main/templates/layout/base.html
 *
 * Depends on (runtime):
 *   - orders/row-expand/open-close.js → openHiddenRow, closeHiddenRow, focusClosedOrderRow
 *
 * Used by:
 *   - core/boot.js
 *   - js/dynamic/render.js → bindOrderRowHandlers
 */

/** Track bound rows in memory only. A data-* flag would serialize into cached HTML and block rebinding. */
const boundOrderRows = window.__boundOrderRows || new WeakSet();
window.__boundOrderRows = boundOrderRows;

/**
 * Attach expand/collapse listeners to every unbound `.visibleRows` element.
 *
 * @returns {void}
 */
function handle_orders() {
  const visibleRows = document.querySelectorAll(".visibleRows");

  visibleRows.forEach((visibleRow) => {
    const row_id = visibleRow.id;
    const hiddenRow = document.getElementById("hidden-row-" + row_id);

    /** Safety check. */
    if (!hiddenRow) return;

    /** Avoid duplicate listeners when new rows are appended (infinite scroll). */
    if (boundOrderRows.has(visibleRow)) return;
    boundOrderRows.add(visibleRow);

    /** Initialize open state from DOM so restored expanded rows fold on first click. */
    hiddenRow._isOpen = hiddenRow.classList.contains("is-open")
      || hiddenRow.classList.contains("orderClicked")
      || hiddenRow.style.display === "block";
    hiddenRow._isClosing = false;
    hiddenRow._isAnimating = false;
    hiddenRow._pendingTransitionHandler = null;

    visibleRow.addEventListener("click", function () {
      if (!hiddenRow._isOpen) {
        openHiddenRow(hiddenRow, row_id, visibleRow);
      } else {
        closeHiddenRow(hiddenRow, visibleRow);
      }
    });

    const closeBtn = hiddenRow.querySelector(".hidden-row-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (hiddenRow._isOpen) {
          closeHiddenRow(hiddenRow, visibleRow);
          focusClosedOrderRow(visibleRow);
        }
      });
    }
  });
}
