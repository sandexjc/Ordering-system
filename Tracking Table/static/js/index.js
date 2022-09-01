//Last change

$(".visibleRows").each(function() {
	$(this).click(function() {
		row_id = this.getAttribute('id');
		$(".hiddenRows").each(function() {
			if (this.getAttribute('id') == row_id) {
				if (this.style.display === 'none') {
					this.style.display = 'block';
					this.classList.add("orderClicked");
				}else{
					this.style.display = 'none';
					this.classList.remove("orderClicked");
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

			context: updateButton,

			success: function(data) {
				$(".ALERT-E").css("display","none");
				$(".ALERT-S").css("display","inline");
				$(this).prop('disabled', false);
				$(this).html("Update");
				$(this).find('span').remove();

				// $('.newCont').replaceWith(data);
				

			},
			error: function() {
				$(".ALERT-E").css("display","inline");
				$(".ALERT-S").css("display","none");
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

		$.ajax({
			method: "POST",
			url: '/table/deleteOrder/' + this.getAttribute('id'),
			data: $("#Delete"+this.getAttribute('id')+" .deleteForms").serialize(),
			success: function() {
				location.reload();
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

// $('#editOrderForm').submit()

$(".SuccessAlertBtn").click(function() {
	console.log("SuccessAlertBtn clicked");
	$(".ALERT-S").css("display","none");
})

$(".ErrorAlertBtn").click(function() {
	$(".ALERT-E").css("display","none");
})

$(".alertmsg").focus();

