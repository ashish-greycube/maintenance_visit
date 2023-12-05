# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils import cint, formatdate, getdate, today,format_datetime,get_weekday,get_user_date_format,add_days
import calendar
from datetime import timedelta
from dateutil import relativedelta
import pandas as pd
from frappe.contacts.doctype.address.address import get_default_address,get_address_display

class MaintenanceVisitScheduleES(Document):
	# def autoname(self):
	# 	self.set_maintenance_visit_schedule() 

	def validate(self):
		if self.is_new()==1:
			self.set_maintenance_visit_schedule() 
		self.total_visits=len(self.get('maintenance_visit_schedule'))
		#  todo : actual date copy from on site? yes
		#  address?
		# pass
		

	def set_maintenance_visit_schedule(self):
		scheduled_date_list=[]
		if self.visit_type=='Scheduled':
			scheduled_date_list=self.get_scheduled_dates(self.contract_start_date,self.contract_end_date,self.scheduled_frequency)
			for scheduled_date in scheduled_date_list:
				scheduled_date=frappe._dict({'scheduled_date':scheduled_date,'scheduled_day':get_weekday(scheduled_date),'scheduled_time':'10:00:00.000000'})
				self.append('maintenance_visit_schedule',scheduled_date)

	def get_scheduled_dates(self,start_date,end_date,frequency):
		dates = []
		# todo frequencey
		# https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
		if frequency == "Daily":
			for date in pd.date_range(start_date, end_date):
				dates.append(date)
		elif frequency == "Weekly":
			for date in pd.date_range(start_date, end_date, freq="W"):
				dates.append(date)
		elif frequency == "Monthly":
			for date in pd.date_range(start_date, end_date, freq="M"):		
				dates.append(date)	
		elif frequency == "Quarterly":
			# freq='3M'
			for date in pd.date_range(start_date, end_date, freq="Q"):
				dates.append(date)
		elif frequency == "Half-Yearly":
			for date in pd.date_range(start_date, end_date, freq="6M"):
				dates.append(date)
		return dates		
	
@frappe.whitelist()
def create_on_site_visit_as_per_schedule():
	create_visit_prior_days = frappe.db.get_single_value('Maintenance Visit Settings ES', 'create_visit_prior_days')
	visit_check_date=add_days(today(), cint(create_visit_prior_days))
	maintenance_visit_schedule_list=frappe.db.get_list('Maintenance Visit Schedule ES', filters={'contract_status':'Active',
													'visit_type':'Scheduled'})
	print(maintenance_visit_schedule_list,visit_check_date)
	for mvs in maintenance_visit_schedule_list:
		print('mvs.name',mvs.name)
		mvs_detail_list=frappe.db.get_list('Maintenance Visit Schedule Detail ES', filters={'parent':mvs.name,
								'scheduled_date':['between',[today(),visit_check_date]],
								'on_site_visit_reference':''
								},fields=['parent','name','scheduled_date','on_site_visit_reference','idx','scheduled_time'],order_by='scheduled_date asc')	
		print(mvs_detail_list)	
		for mvs_detail in mvs_detail_list:
			# create a new document
			print(mvs_detail.parent,'mvs_detail.parent')
			doc = frappe.new_doc('On Site Visit ES')
			doc.visit_schedule_reference=mvs_detail.get('parent')
			doc.visit_date=mvs_detail.get('scheduled_date')
			doc.visit_time=mvs_detail.get('scheduled_time') or '10:00:00.000000'
			doc.visit_status='Open'
			doc.visit_reason='Scheduled'
			doc.visit_schedule_detail_hex=mvs_detail.name
			sales_order_name = frappe.db.get_value('Maintenance Visit Schedule ES', mvs_detail.parent, 'sales_order')
			print('sales_order_name',sales_order_name)
			if sales_order_name:
				doc.sales_order=sales_order_name
				sales_order=frappe.get_doc('Sales Order',sales_order_name)
				for so_item in sales_order.get('items'):
					service_item=doc.append('service_activites')
					service_item.item_code=so_item.item_code
					service_item.item_name=so_item.item_name
					service_item.qty=so_item.qty
					# service_item.activity_status=
			doc.run_method('set_missing_values')
			doc.save(ignore_permissions=True)					
			doc.add_comment('Comment', text='Auto created by nightly job for {0}: Row No {1} on {2}'.format(mvs.name,mvs_detail.idx,today()))
			frappe.db.set_value('Maintenance Visit Schedule Detail ES', mvs_detail.name, 'on_site_visit_reference', doc.name)
			frappe.db.set_value('Maintenance Visit Schedule Detail ES', mvs_detail.name, 'status', doc.visit_status)
			print(doc.name)


@frappe.whitelist()
def get_customer_address(customer_name):
	default_address=get_default_address('Customer',customer_name)
	print(default_address,'default_address')
	if default_address:
		address_display = ""
		address = frappe.get_doc("Address", default_address)
		address_display=get_condensed_address(address)
	print('address_display',address_display)	
	return address_display

def get_condensed_address(doc):
	fields = ["address_title", "address_line1", "address_line2", "city", "county", "state", "country","pincode"]
	return "\n ".join([doc.get(d) for d in fields if doc.get(d)])
