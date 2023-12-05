# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, formatdate, getdate, today,get_weekday

class OnDemandVisitRequestES(Document):
	def on_submit(self):
			doc = frappe.new_doc('On Site Visit ES')
			doc.visit_schedule_reference=self.maintenance_visit_schedule
			doc.visit_date=self.visit_date
			doc.visit_time=self.visit_time
			doc.on_demand_visit_request_reference=self.name
			# todo  contact, phone <-- copy to On site?
			doc.visit_reason=self.visit_reason
			doc.visit_status='Open'
			doc.run_method('set_missing_values')
			doc.save(ignore_permissions=True)
			doc.add_comment('Comment', text='Auto created by on demand visit request {0} on {1}'.format(self.name,today()))

			mvs=frappe.get_doc('Maintenance Visit Schedule ES',self.maintenance_visit_schedule)
			mvs_detail_row=mvs.append('maintenance_visit_schedule',{})
			mvs_detail_row.scheduled_date=self.visit_date
			mvs_detail_row.scheduled_time=self.visit_time
			mvs_detail_row.scheduled_day=get_weekday(getdate(self.visit_date))
			mvs_detail_row.status='Open'
			mvs_detail_row.on_demand_visit_ref=self.name
			mvs_detail_row.on_site_visit_reference=doc.name
			mvs.save(ignore_permissions=True)
			# mvs.add_comment('Comment', text='Auto created  row no {0} for on demand visit request {1}'.format(mvs_detail_row.idx,self.name))
			mvs_detail_list=frappe.db.get_list('Maintenance Visit Schedule Detail ES', 
									  filters={'on_demand_visit_ref':self.name,'on_site_visit_reference':doc.name},fields=['name','idx'])	
			if mvs_detail_list and len(mvs_detail_list)>0:
				mvs.add_comment('Comment', text='Auto created  row no {0} for on demand visit request {1}'.format(mvs_detail_list[0].idx,self.name))
				frappe.db.set_value('On Site Visit ES', doc.name, 'visit_schedule_detail_hex', mvs_detail_list[0].name)
				frappe.db.set_value('On Demand Visit Request ES', self.name, 'on_site_visit_reference', doc.name)
				frappe.db.set_value('On Demand Visit Request ES', self.name, 'on_site_visit_reference', 'Open')
				frappe.db.set_value('On Demand Visit Request ES', self.name, 'visit_schedule_detail_hex', mvs_detail_list[0].name)


						