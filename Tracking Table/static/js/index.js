function base() {
	$(".visibleRows").each(function() {
		$(this).click(function() {
			row_id = this.getAttribute('id');
			$(".hiddenRows").each(function() {
				if (this.getAttribute('id') === row_id) {
					if (this.style.display === 'none') {
						this.style.display = 'block';
						this.classList.add("orderClicked");
						$("#"+row_id+".visibleRows").addClass("rowSelected");
						$(this).focus();
						fetch('/viewOrder/' + row_id)
							.then((response) => {
								return response.text()
							})
							.then((html) => {
								let parser = new DOMParser();
								let newHtml = parser.parseFromString(html, 'text/html');
								/** Load modal progress window */
								document.body.innerHTML += newHtml.getElementById("progress-window-"+row_id).innerHTML;
								/** Load modal delete window */
								document.body.innerHTML += newHtml.getElementById("delete-window-"+row_id).innerHTML;
								/** Load offcanvas history tab */
								document.body.innerHTML += newHtml.getElementById("offcanvas-history-tab-"+row_id).innerHTML;
								/** Load order table */
								document.getElementById("hidden-table-"+row_id)
									.innerHTML = newHtml.getElementsByClassName("order-view")[0].innerHTML;
								/** Attach event handlers */
								addOrderBtnHandlers();
								addHistoryBtnHandlers();
								base();
							})
							.catch((error) => console.error('Error:', error));
					}else{
						this.style.display = 'none';
						this.classList.remove("orderClicked");
						$("#"+row_id+".visibleRows").removeClass("rowSelected");
					}
				}
			})
		})
	});
}

base();