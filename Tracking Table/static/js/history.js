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
				historyBtn_body.find('div').remove();
				historyBtn_body.find('span').remove();
				// console.log(data);

				$.each(data, function() {
					$.each(this, function() {
						historyBtn_body.append('<div class="historyEntry" style="font-size: 10px;"></div');
						$('.historyEntry').append('<br>');
						$.each(this.fields, function() {

							$('.historyEntry').append(this + ' ');
							console.log(this);
							
						})
					})
				})

			},

			error: function(status) {
				$('#'+this.getAttribute("id")+'.offcanvas-body').find('div').remove();
				$('#'+this.getAttribute("id")+'.offcanvas-body').find('span').remove();
				console.log(status.statusText);
			}
		})
	})
})