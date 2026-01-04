/**
 * All order properties and events handling
 */

function handle_orders_properties() 
{
	$(".updateButtons").each(function() {
		$(this).click(function() {

			$(this).prop('disabled', true);
			$(this).html("Loading...");
			$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
			var updateButton = this;

			$.ajax({
				method: "POST",
				url: '/table/updateOrder/' + this.getAttribute('id'),
				data: $("#modal-progress-"+this.getAttribute('id')+" .updateForms").serialize(),
				timeout: 10000,
				context: updateButton,

				success: function(data) {
					$(".ALERT-E-UPD-VIEW").css("display","none");
					$(".ALERT-S-UPD-VIEW").css("display","inline");
					$(this).prop('disabled', false);
					$(this).html("Update");
					$(this).find('span').remove();

					$(data.order).each(function() {
						if (this.fields.order_taken == true) {
							$("#"+this.pk+".visibleRows").removeClass('normalOrder');
							$("#"+this.pk+".visibleRows").addClass('orderTaken');
						}else{
							$("#"+this.pk+".visibleRows").removeClass('orderTaken');
							$("#"+this.pk+".visibleRows").addClass('normalOrder');
						}

						if (this.fields.invoice == true) {
							$("#ID"+this.pk).css('color', 'red');
						}else{
							$("#ID"+this.pk).css('color', 'black');
						}
					})

					$(data.plates).each(function() {

						if ((this.fields.ordered == true) && (this.fields.from_client != true) && (this.fields.delivered != true)) {
							$("#plate"+this.pk).css('color', 'red');
						}else if (this.fields.delivered == true) {
							$("#plate"+this.pk).css('color', '#8ac926');
						}else if (this.fields.from_client == true) {
							$("#plate"+this.pk).css('color', '#7b2cbf');
						}else{
							$("#plate"+this.pk).css('color', 'black');
						}

						if ((this.fields.ordered == true) && (this.fields.from_client != true)) {
							$("#plate-progress-ordered-"+this.pk).addClass("active");
						}else{
							$("#plate-progress-ordered-"+this.pk).removeClass("active");
						}

						if (this.fields.delivered == true) {
							$("#plate-progress-delivered-"+this.pk).addClass("active");
						}else{
							$("#plate-progress-delivered-"+this.pk).removeClass("active");
						}

						if (this.fields.cutted == true) {
							$("#plate-progress-cutted-"+this.pk).addClass("active");
						}else{
							$("#plate-progress-cutted-"+this.pk).removeClass("active");
						}

						if (this.fields.edged == true) {
							$("#plate-progress-edged-"+this.pk).addClass("active");
						}else{
							$("#plate-progress-edged-"+this.pk).removeClass("active");
						}
					})

					$(data.edges).each(function() {
						if ((this.fields.ordered == true) && (this.fields.delivered != true)) {
							$("#edge"+this.pk).css('color', 'red');
						}else if ((this.fields.ordered == true) && (this.fields.delivered == true)) {
							$("#edge"+this.pk).css('color', '#8ac926');
						}else{
							$("#edge"+this.pk).css('color', 'black');
						}

						if (this.fields.ordered == true) {
							$("#edge-progress-ordered-"+this.pk).addClass("active");
						}else{
							$("#edge-progress-ordered-"+this.pk).removeClass("active");					
						}

						if (this.fields.delivered == true) {
							$("#edge-progress-delivered-"+this.pk).addClass("active");
						}else{
							$("#edge-progress-delivered-"+this.pk).removeClass("active");	
						}
					})
				},
				error: function(status) {
					$(".alertmsgdiv").find("div").remove();
					$(".alertmsgdiv").append("<div>"+status.statusText+"</div>");
					$(".ALERT-E-UPD-VIEW").css("display","inline");
					$(".ALERT-S-UPD-VIEW").css("display","none");
					$(this).prop('disabled', false);
					$(this).html("Update");
					$(this).find('span').remove();
				}

				})
		})
	})

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