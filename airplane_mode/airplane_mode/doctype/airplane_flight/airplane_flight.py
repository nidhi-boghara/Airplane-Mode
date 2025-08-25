# Copyright (c) 2025, Nidhi and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.document import Document


class AirplaneFlight(WebsiteGenerator):
	
	def on_submit(self):
		print('on submit call-----------------------------')
		self.status = "Completed"

	def on_cancel(self):
		self.status = "Cancelled"

def update_gate_number(doc,method):
	if doc.gate_number:
		tickets = frappe.get_all("Airplane Ticket", filters={"flight": doc.name}, fields=["name"])
		if tickets:
			for ticket in tickets:
				ticket_doc = frappe.get_doc("Airplane Ticket", ticket["name"])
				ticket_doc.gate_number = doc.gate_number
				ticket_doc.save()

			frappe.msgprint(f"Gate number updated in all linked tickets for flight {doc.name}.")