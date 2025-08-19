# Copyright (c) 2025, Nidhi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class RentPayment(Document):
	
	def before_submit(self):
		self.status = "Paid"
	
	def on_submit(self):
		lease = frappe.get_doc("Lease Contract", self.lease_contract)
		updated = False

		# Convert payment_date to date object
		if isinstance(self.payment_date, str):
			payment_date = datetime.strptime(self.payment_date, "%Y-%m-%d").date()
		else:
			payment_date = self.payment_date

		for row in lease.payment_schedule:
			# Convert row.due_date to date object
			if isinstance(row.due_date, str):
				due_date = datetime.strptime(row.due_date, "%Y-%m-%d").date()
			else:
				due_date = row.due_date

			if due_date == payment_date:
				frappe.db.set_value("Payment Schedule Details", row.name, "status", "Paid")
				frappe.db.set_value("Payment Schedule Details", row.name, "payment_reference", self.name)
				frappe.db.commit()
				updated = True
				break

		if updated:		
			frappe.msgprint(f"Payment schedule updated for Lease {lease.name}")
		else:
			frappe.msgprint(f"No matching due date found in Lease {lease.name}")
