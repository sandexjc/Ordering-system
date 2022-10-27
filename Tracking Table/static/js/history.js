$('.Historybtns').each(function() {
	$(this).click(function() {
		var historyBtn = this;
		var historyBtn_id = this.getAttribute('id')
		var historyBtn_body = $('#'+this.getAttribute("id")+'.offcanvas-body')
		
		$.ajax({
			method: "GET",
			url: '/table/getOrderHistory/' + this.getAttribute('id'),
			timeout: 10000,
			context: historyBtn,

			success: function(data) {
				historyBtn_body.empty();
				historyBtn_body.find('div').remove();
				historyBtn_body.find('span').remove();
				historyBtn_body.css({
					'font-size':'10px',
					'font-weight':'bold',
					});
				historyBtn_body.append("<br>");
			
				$.each(data, function() {
					$.each(this, function() {

							historyBtn_body.append(this.fields.date + " ");
							historyBtn_body.append(this.fields.user + " ");
							historyBtn_body.append(this.fields.operation + " ");
							historyBtn_body.append(this.fields.what + " ");
							historyBtn_body.append(this.fields.current_state + " ");
							historyBtn_body.append(this.fields.new_state + " ");
							historyBtn_body.append("<br>");

					})
				})

			},

			error: function(status) {
				$('#'+this.getAttribute("id")+'.offcanvas-body').find('div').remove();
				$('#'+this.getAttribute("id")+'.offcanvas-body').find('span').remove();
				historyBtn_body.append("<br>");
				historyBtn_body.append(status.statusText);
				historyBtn_body.css({
					'margin-top': '100%',
					});
			}
		})
	})
})