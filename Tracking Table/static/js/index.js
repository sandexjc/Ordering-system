var clickable_rows = document.getElementsByClassName('visibleRows');
var hidden_rows = document.getElementsByClassName('hiddenRows');

$("#demo").html("Hello World");

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

// $(".visibleRows").each(function() {
// 	$(this).click(function() {

// 		console.log(this.style.backgroundColor);

// 		if (this.style.backgroundColor === "white") {
// 			$(this).css("backgroundColor", "#e5e5e5");
// 		}else{
// 			$(this).css("backgroundColor", "white");
// 		}

// 		var row_id = this.getAttribute('id');

// 		$(".hiddenRows").each(function() {
// 			if (this.getAttribute('id') === row_id) {
// 				if (this.style.display === 'none') {
// 					$(this).css("display", "block");
// 					$(this).css("backgroundColor", "#e5e5e5");
// 				}else{
// 					$(this).css("display", "none");
// 					$(this).css("backgroundColor", document.body.style.backgroundColor);
// 				}
// 			}
// 		})
// 	})
// })

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

					})
			}
		})
	})
})

$(".closeAlert").click(function() {
	$(".ALERT-S").css("display","none");
})