/**
 * All order properties and events handling
 */

function handle_orders_properties() 
{
	/**
	 * UPDATE (progress form) handler
	 * Works for table + vitrine
	 * Vanilla JS, delegated, app-agnostic
	 */

	/** Remove old handler if already registered */
	if (window.updateHandler) {
		document.removeEventListener("click", window.updateHandler);
	}

	/** Create a single delegated handler */
	window.updateHandler = function (event) {
		const btn = event.target.closest(".btn-update");
		if (!btn) return;

		event.preventDefault();

		const url = btn.dataset.url;
		const id = btn.dataset.id;

		const modal = btn.closest(".modal");
		if (!modal) return;

		const form = modal.querySelector("form");
		if (!form) return;

		/** Loading state */
		btn.disabled = true;
		const oldHtml = btn.innerHTML;
		btn.innerHTML = `Loading... <span class="spinner-border spinner-border-sm" role="status"></span>`;

		const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
		const formData = new FormData(form);

		fetch(url, {
			method: "POST",
			headers: { "X-CSRFToken": csrfToken },
			body: formData
		})
		.then(r => r.json().then(d => ({ ok: r.ok, data: d })))
		.then(result => {
			if (!result.ok) {
				throw new Error("Update failed");
			}

			/** Alerts */
			document.querySelectorAll(".ALERT-E-UPD-VIEW").forEach(el => el.style.display = "none");
			document.querySelectorAll(".ALERT-S-UPD-VIEW").forEach(el => el.style.display = "inline");

			/** Restore button */
			btn.disabled = false;
			btn.innerHTML = "Update";

			const data = result.data || {};

			/** =========================
			 * ORDERS
			 * ========================= */
			if (Array.isArray(data.order)) {
				data.order.forEach(o => {
					const row = document.getElementById(o.pk);

					if (row) {
						row.classList.toggle("orderTaken", o.fields.order_taken === true);
						row.classList.toggle("normalOrder", o.fields.order_taken !== true);
					}

					const idLabel = document.getElementById(`ID${o.pk}`);
					if (idLabel) {
						idLabel.style.color = o.fields.invoice ? "red" : "black";
					}
				});
			}

			/** =========================
			 * PLATES (table app only)
			 * ========================= */
			if (Array.isArray(data.plates)) {
				data.plates.forEach(p => {
					const plate = document.getElementById(`plate${p.pk}`);
					if (plate) {
						if (p.fields.ordered && !p.fields.from_client && !p.fields.delivered) {
							plate.style.color = "red";
						} else if (p.fields.delivered) {
							plate.style.color = "#8ac926";
						} else if (p.fields.from_client) {
							plate.style.color = "#7b2cbf";
						} else {
							plate.style.color = "black";
						}
					}

					const plateStates = ["ordered", "delivered", "cutted", "edged"];
					plateStates.forEach(state => {
						const el = document.getElementById(`plate-progress-${state}-${p.pk}`);
						if (el) {
							el.classList.toggle("active", p.fields[state] === true);
						}
					});
				});
			}

			/** =========================
			 * EDGES (table app only)
			 * ========================= */
			if (Array.isArray(data.edges)) {
				data.edges.forEach(e => {
					const edge = document.getElementById(`edge${e.pk}`);
					if (edge) {
						if (e.fields.ordered && !e.fields.delivered) {
							edge.style.color = "red";
						} else if (e.fields.delivered) {
							edge.style.color = "#8ac926";
						} else {
							edge.style.color = "black";
						}
					}

					["ordered", "delivered"].forEach(state => {
						const el = document.getElementById(`edge-progress-${state}-${e.pk}`);
						if (el) {
							el.classList.toggle("active", e.fields[state] === true);
						}
					});
				});
			}
		})
		.catch(err => {
			console.error(err);

			document.querySelectorAll(".ALERT-E-UPD-VIEW").forEach(el => el.style.display = "inline");
			document.querySelectorAll(".ALERT-S-UPD-VIEW").forEach(el => el.style.display = "none");

			btn.disabled = false;
			btn.innerHTML = oldHtml;
		});
	};

	/** Attach handler */
	document.addEventListener("click", window.updateHandler);


	/** Remove old window delete listener if already registered */
	if (window.deleteHandler) {
		document.removeEventListener("click", window.deleteHandler);
	}

	/** Create a single handler function and store it globally */
	window.deleteHandler = function(event) {
		const btn = event.target.closest(".btn-delete");
		if (!btn) return;

		event.preventDefault();

		const id = btn.dataset.id;
		const url = btn.dataset.url;
		const form = btn.closest("form");

		/** UI loading state */
		btn.disabled = true;
		const oldHtml = btn.innerHTML;
		btn.innerHTML = `Loading... <span class="spinner-border spinner-border-sm"></span>`;

		const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
		const formData = new FormData(form);

		fetch(url, {
			method: "POST",
			headers: { "X-CSRFToken": csrfToken },
			body: formData
		})
		.then(r => r.json().then(d => ({ ok: r.ok, data: d })))
		.then(result => {
			if (!result.ok || result.data.status !== "ok") {
				throw new Error(result.data.message || "Deletion error");
			}

			/** Close modal */
			const modal = document.getElementById(`modal-delete-${id}`);
			if (modal) bootstrap.Modal.getInstance(modal).hide();

			/** Remove HTML elements */
			[
				`#hidden-row-${id}`,
				`[data-row="${id}"]`,
				`#delete-window-${id}`,
				`#progress-window-${id}`,
				`#offcanvas-history-tab-${id}`
			].forEach(sel => document.querySelector(sel)?.remove());
		})
		.catch(err => {
			console.error(err);
			alert("Error deleting item. Please try again.");

			btn.disabled = false;
			btn.innerHTML = oldHtml;
		});
	};

	/** Attach the order delete handler */
	document.addEventListener("click", window.deleteHandler);

	$('#edit-order-button').click(function() {
		$('#edit-order-form').submit();
		$(this).html("Loading...");
		$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
		$(this).prop('disabled', true);
	})

	$('#edit-vitrine-button').click(function() {
		$('#edit-vitrine-form').submit();
		$(this).html("Loading...");
		$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
		$(this).prop('disabled', true);
	})

	$(".SuccessAlertBtn").click(function() {
		$(".ALERT-S-UPD-VIEW").css("display","none");
		$(".ALERT-S-DEL-VIEW").css("display","none");
	})

	$(".ErrorAlertBtn").click(function() {
		$(".ALERT-E-UPD-VIEW").css("display","none");
		$(".ALERT-E-DEL-VIEW").css("display","none");
	})

	$(".alertmsg").focus();
}