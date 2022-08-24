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
		console.log("Button clicked", this.getAttribute('id'));
		var btn_id = this.getAttribute('id');
		// GETTING FORMS SYNCH
		$(".updateForms").each(function() {
			if (this.getAttribute("id") === btn_id) {
				console.log("FORM TO BE SEND", this.getAttribute("id"));
				// SENDING POST REQUEST
				var serializedData = $(this).serialize();
				$.ajax({
					method: "POST",
					url: '/table/updateOrder/' + this.getAttribute('id'),
					data: serializedData,
					success: function() {
						$(".ALERT-S").css("display","inline");
					},
					error: function() {
						$(".ALERT-E").css("display","inline");
					}

					})
			}
		})
	})
})

$(".SuccessAlertBtn").click(function() {
	console.log("SuccessAlertBtn clicked");
	$(".ALERT-S").css("display","none");
})

$(".ErrorAlertBtn").click(function() {
	$(".ALERT-E").css("display","none");
})

