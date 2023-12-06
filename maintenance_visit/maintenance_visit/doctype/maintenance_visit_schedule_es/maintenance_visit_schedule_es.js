// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Visit Schedule ES', {
	onload: function(frm){
		frm.set_query('sales_order', () => {
			return {
				filters: {
					customer: frm.doc.customer,
					docstatus:1
				}
			}
		})
	},
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
				}else{
					frm.set_value('customer_address','')
				}
			})			
		}

	}
});

frappe.ui.form.on('Maintenance Visit Schedule Detail ES', {
	before_maintenance_visit_schedule_remove: function(frm,cdt,cdn){
		let row=locals[cdt][cdn]
		if (row.on_site_visit_reference || row.on_demand_visit_ref) {
			frappe.throw(__('Cannot delete, as On Site Ref/On Demand Ref is generated'))

		}

	},
	scheduled_date: function(frm,cdt,cdn){
		let row=locals[cdt][cdn]
		if (row.scheduled_date) {
			var a = new Date(row.scheduled_date);
			var weekdays=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
			row.scheduled_day=weekdays[a.getDay()]
			frm.refresh_field('maintenance_visit_schedule')
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


