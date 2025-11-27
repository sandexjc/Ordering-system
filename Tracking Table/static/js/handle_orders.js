/* -----------------------------
   Utilities (internal helpers)
   ----------------------------- */

// Remove any previously registered transition handler and lock current px height
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
  const computedHeight = cs.height;
  hiddenRow.style.height = computedHeight;
}

/* -----------------------------
   Event delegation: main entry
   ----------------------------- */
function handle_orders() {

  document.addEventListener("click", function (event) {

    const row = event.target.closest(".visibleRows");
    if (!row) return;

    const row_id = row.id;
    const targetId = "hidden-row-" + row_id;
    const visibleRow = document.querySelector(`.visibleRows[id="${row_id}"]`);
    const hiddenRows = document.querySelectorAll(".hiddenRows");

    hiddenRows.forEach((hiddenRow) => {
      if (hiddenRow.id !== targetId) return;

      const cs = window.getComputedStyle(hiddenRow);
      const isClosed = cs.display === "none" || cs.height === "0px";

      if (isClosed) {
        openHiddenRow(hiddenRow, row_id, visibleRow);
      } else {
        closeHiddenRow(hiddenRow, visibleRow);
      }
    });
  });
}


/* -----------------------------
   OPEN ROW — robust smooth expand
   ----------------------------- */
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
  const startHeightCss = window.getComputedStyle(hiddenRow).height || "0px";
  // If currently not 0 (e.g., we locked to some px), we start from that; otherwise zero
  if (startHeightCss === "0px") {
    hiddenRow.style.height = "0px";
  } else {
    hiddenRow.style.height = startHeightCss;
  }

  // Force reflow so the start height is applied
  hiddenRow.getBoundingClientRect();

  // Target height is the scrollHeight (content height)
  const targetHeight = hiddenRow.scrollHeight + "px";

  // add transitionend handler — ensure only one is attached and it's removable
  const openHandler = function (e) {
    if (e.target !== hiddenRow || e.propertyName !== "height") return;
    // finalize
    hiddenRow.style.height = "auto";
    hiddenRow._isAnimating = false;
    hiddenRow._pendingTransitionHandler = null;
    hiddenRow.classList.add("is-open");
    hiddenRow.removeEventListener("transitionend", openHandler);
  };

  // store and attach handler
  hiddenRow._pendingTransitionHandler = openHandler;
  hiddenRow._isAnimating = true;
  hiddenRow.addEventListener("transitionend", openHandler);

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
  }
}


/* -----------------------------
   CLOSE ROW — robust smooth collapse
   ----------------------------- */
function closeHiddenRow(hiddenRow, visibleRow) {

  // Cancel prior handlers and lock current visual height (so transition starts from visible height)
  _cancelPendingTransitionAndLockHeight(hiddenRow);

  hiddenRow.classList.add("is-closing");
  hiddenRow._isClosing = true;

  // If height is 'auto' or blank, set it to the measured px so the transition can animate from there
  const cs = window.getComputedStyle(hiddenRow);
  if (cs.height === "auto" || hiddenRow.style.height === "") {
    hiddenRow.style.height = hiddenRow.scrollHeight + "px";
  }

  // Force layout so the locked height applies
  hiddenRow.getBoundingClientRect();

  // Create a single close handler
  const closeHandler = function (e) {
    if (e.target !== hiddenRow || e.propertyName !== "height") return;
    // finalize close
    hiddenRow.style.display = "none";
    hiddenRow.style.height = "0px";
    hiddenRow.classList.remove("is-closing");
    hiddenRow._isClosing = false;
    hiddenRow._isAnimating = false;
    hiddenRow._pendingTransitionHandler = null;
    hiddenRow.classList.remove("is-open");
    hiddenRow.removeEventListener("transitionend", closeHandler);
  };

  // attach handler & mark animating
  hiddenRow._pendingTransitionHandler = closeHandler;
  hiddenRow._isAnimating = true;
  hiddenRow.addEventListener("transitionend", closeHandler);

  // trigger collapse on next frame
  requestAnimationFrame(() => {
    hiddenRow.style.height = "0px";
  });

  hiddenRow.classList.remove("orderClicked");
  if (visibleRow) visibleRow.classList.remove("rowSelected");
}


/* ---------------------------------------------------------
   After dynamic content is loaded → expand row smoothly
   (only act when the row is not closing)
   --------------------------------------------------------- */
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
    hiddenRow.removeEventListener("transitionend", updateHandler);
  };

  hiddenRow._pendingTransitionHandler = updateHandler;
  hiddenRow._isAnimating = true;
  hiddenRow.addEventListener("transitionend", updateHandler);

  // animate to new height
  requestAnimationFrame(() => {
    hiddenRow.style.height = newHeight + "px";
  });
}
