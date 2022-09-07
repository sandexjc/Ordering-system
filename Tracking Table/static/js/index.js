//Last change

$(".visibleRows").each(function() {
	$(this).click(function() {
		row_id = this.getAttribute('id');
		$(".hiddenRows").each(function() {
			if (this.getAttribute('id') == row_id) {
				if (this.style.display === 'none') {
					this.style.display = 'block';
					this.classList.add("orderClicked");
					$("#"+row_id+".visibleRows").addClass("rowSelected");
					$(this).focus();
				}else{
					this.style.display = 'none';
					this.classList.remove("orderClicked");
					$("#"+row_id+".visibleRows").removeClass("rowSelected");
				}
			}
		})
	})
})

$(".updateButtons").each(function() {
	$(this).click(function() {

		$(this).prop('disabled', true);
		$(this).html("Loading...");
		$(this).append('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
		var updateButton = this;

		$.ajax({
			method: "POST",
			url: '/table/updateOrder/' + this.getAttribute('id'),
			data: $("#Progress"+this.getAttribute('id')+" .updateForms").serialize(),
			timeout: 10000,

			context: updateButton,

			success: function(data) {
				$(".ALERT-E-UPD-VIEW").css("display","none");
				$(".ALERT-S-UPD-VIEW").css("display","inline");
				$(this).prop('disabled', false);
				$(this).html("Update");
				$(this).find('span').remove();
				console.log(data.updated_object);
				

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
		var deleteButton = this

		$.ajax({
			method: "POST",
			url: '/table/deleteOrder/' + this.getAttribute('id'),
			data: $("#Delete"+this.getAttribute('id')+" .deleteForms").serialize(),
			timeout: 10000,
			context: deleteButton,
			success: function(data) {
				$("#Delete"+this.getAttribute('id')+".modal").modal('hide');
				$("#"+this.getAttribute('id')+".visibleRows").remove();
				$("#"+this.getAttribute('id')+".hiddenRows").remove();

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

$('#editButton').click(function() {
	$('#editOrderForm').submit();
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

