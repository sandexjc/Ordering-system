var clickable_rows = document.getElementsByClassName('click');
var hidden_rows = document.getElementsByClassName('hidden');
var hidden_alert = document.getElementsByClassName("ALERT-S");
var alert_button = document.getElementsByClassName("showAlert");
var alert_close_btn = document.getElementsByClassName("closeAlert");

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

alert_button[0].addEventListener('click', function() {
	console.log('SHOW ALERT CLICKED');
	hidden_alert[0].style.display = "inline";
	console.log(hidden_alert[0].style.display);
})

alert_close_btn[0].addEventListener('click', function() {
	console.log('BUTTON CLOSED');
	hidden_alert[0].style.display = 'none';
	console.log(hidden_alert[0].style.display);
})