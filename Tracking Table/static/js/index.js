var clickable_rows = document.getElementsByClassName('visibleRows');
var hidden_rows = document.getElementsByClassName('hiddenRows');

for (var i=0; i<clickable_rows.length; i++) {
	clickable_rows[i].addEventListener('click', function() {
		for (var k=0; k<hidden_rows.length; k++) {
			if (hidden_rows[k].getAttribute('id') === this.getAttribute('id')) {
				if (hidden_rows[k].style.display === 'none') {
					hidden_rows[k].style.display = 'block';
					this.style.backgroundColor = '#e5e5e5';
					console.log(this.id)
				}else{
					hidden_rows[k].style.display = 'none';
					this.style.backgroundColor = document.body.style.backgroundColor;
				}
			}
		}
	});
}

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

			success: function() {
				$(".ALERT-E").css("display","none");
				$(".ALERT-S").css("display","inline");
				$(this).prop('disabled', false);
				$(this).html("Update");
				$(this).find('span').remove();
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

