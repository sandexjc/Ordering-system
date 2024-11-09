/**
 * Add all orders events and callbacks
 * Handle table rows events
 */

function handle_orders() 
{
	$(".visibleRows").each(function() {
		$(this).click(function() {
			row_id = this.getAttribute('id');
			$(".hiddenRows").each(function() {
				if (this.getAttribute('id') === "hidden-row-" + row_id) {
					if (this.style.display === 'none') {
						this.style.display = 'block';
						this.classList.add("orderClicked");
						$("#"+row_id+".visibleRows").addClass("rowSelected");
						$(this).focus();
                        if (!this.classList.contains("fetch-prevent"))
                        {
							/** add loading indication */
                            document.getElementById("hidden-row-" + row_id).appendChild(spinner(row_id));
							/** prevent duplicate requests on click event */
							document.getElementById("hidden-row-" + row_id).classList.add("fetch-prevent");
							/** get order information and actions */
                            get_order(row_id);
                        }
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