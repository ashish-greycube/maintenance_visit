// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Visit Schedule ES', {
	validate: function(frm) {
		if (frm.is_new()==1) {
			return wait(frm)
		}
	},
	customer: function(frm) {
		if (frm.doc.customer) {
			frappe.call('maintenance_visit.maintenance_visit.doctype.maintenance_visit_schedule_es.maintenance_visit_schedule_es.get_customer_address', {
				customer_name: frm.doc.customer
			}).then(r => {
				console.log(r.message)
				if (r.message) {
					frm.set_value('customer_address',r.message)
				}
			})			
		}

	}
});

function wait(frm) {
	return new Promise((resolve, reject) => {
		frappe.confirm('Visit Type  & Scheduled Frequency , once set cannot be changed.<br>Are you sure you want to proceed?',
    () => {
        // action to perform if Yes is selected
		resolve()
    }, () => {
        // action to perform if No is selected
		reject()
    })

	})	
}


