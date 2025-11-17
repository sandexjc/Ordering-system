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

	$('.deleteButtons').each(function() {
		$(this).click(function() {
			$(this).prop('disabled', true);
			$(this).html("Loading...");
			$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
			var deleteButton = this;
			var order_id = this.getAttribute('id');

			$.ajax({
				method: "POST",
				url: '/table/deleteOrder/' + this.getAttribute('id'),
				data: $("#modal-delete-"+this.getAttribute('id')+" .deleteForms").serialize(),
				timeout: 10000,
				context: deleteButton,

				success: function(data) {
					$("#modal-delete-"+this.getAttribute('id')+".modal").modal('hide');
					$("#"+this.getAttribute('id')+".visibleRows").remove();
					document.getElementById("modal-progress-" + order_id).remove();
					document.getElementById("history-tab-" + order_id).remove();
					document.getElementById("hidden-row-" + order_id).remove();
					document.getElementById("modal-delete-" + order_id).remove();
				},

				error: function(status) {
					$(".alertmsgdiv").find("div").remove();
					$(".alertmsgdiv").append("<div>"+status.statusText+"</div>");
					$(".ALERT-E-DEL-VIEW").css("display","inline");
					$(".ALERT-S-DEL-VIEW").css("display","none");
					$(this).prop('disabled', false);
					$(this).html("Confirm");
					$(this).find('span').remove();
				}
			})
		})
	})

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