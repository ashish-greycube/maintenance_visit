// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Site Visit ES', {
	onload: function(frm) {
		frm.set_query('item_code', 'consumed_materials', () => {
			return {
				filters: {
					is_stock_item: 1
				}
			}
		})		
	}
});
