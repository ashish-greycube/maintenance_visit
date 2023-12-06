// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Demand Visit Request ES', {
	onload: function(frm) {
		frm.set_query('maintenance_visit_schedule', () => {
			return {
				filters: {
					visit_type: 'Random',
					contract_status : 'Active',
					customer:frm.doc.customer
				}
			}
		})
		
	}
});
