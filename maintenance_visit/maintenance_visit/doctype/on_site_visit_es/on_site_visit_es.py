# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext import get_company_currency, get_default_company
from frappe.utils import getdate, cstr, flt

class OnSiteVisitES(Document):
	def validate(self):
		if self.visit_status=='Completed':
			for service_activity in self.service_activites:
				if service_activity.activity_status!='Completed':
					frappe.throw(title='Incorrect service acitivity status', msg='All service activity should be completed.  <br>  Please correct Row: {0} to proceed..'
				  .format(frappe.bold(service_activity.idx)))

	def on_submit(self):
		# todo : stock entry for each item? --> consolidated one
		#  submit doc
		#  address? --> copy from scheudle
		if self.consumed_materials and len(self.consumed_materials)>0:
			material_issue=self.create_material_issue()
			self.material_issue=material_issue
			frappe.db.set_value('On Site Visit ES', self.name, 'material_issue', material_issue) 
		# copy visit_date back
		print(self.visit_schedule_detail_hex,self.visit_status,self.on_demand_visit_request_reference)
		frappe.db.set_value('Maintenance Visit Schedule Detail ES', self.visit_schedule_detail_hex, 'status', self.visit_status) 
		frappe.db.set_value('Maintenance Visit Schedule Detail ES', self.visit_schedule_detail_hex, 'actual_date', self.visit_date)
		frappe.db.set_value('On Demand Visit Request ES', self.on_demand_visit_request_reference, 'on_site_visit_status', self.visit_status)


		


	def create_material_issue(self):
	# create a new Material Transfer document
		se = frappe.new_doc("Stock Entry")
		se.purpose = "Material Issue"
		se.set_stock_entry_type()	
		se.company = get_default_company()
		for consumed_material in self.consumed_materials:
			item1 = se.append('items')
			item1.item_code = consumed_material.item_code
			item1.item_name = consumed_material.item_name
			item1.uom = frappe.db.get_value("Item", consumed_material.item_code, "stock_uom")
			item1.stock_uom = item1.uom
			item1.qty = flt( consumed_material.qty)
			# in stock uom
			item1.conversion_factor = 1		
			# item1.allow_zero_valuation_rate=1	
			item1.qty = consumed_material.qty
			item1.s_warehouse = consumed_material.warehouse
		se.run_method('set_missing_values')
		se.save(ignore_permissions=True)	
		se.submit()
		# return the name of the Material issue document
		return se.name