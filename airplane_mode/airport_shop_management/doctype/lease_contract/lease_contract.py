# Copyright (c) 2025, Nidhi and contributors
# For license information, please see license.txt

import frappe
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days
from datetime import timedelta,datetime

class LeaseContract(Document):
	
	def validate(self):
		
		# Validate contract dates
		if self.contract_start and self.contract_end:
			contract_start_date = getdate(self.contract_start)
			contract_end_date = getdate(self.contract_end)
			
			# Ensure contract_end is at least one year after contract_start
			if contract_end_date < contract_start_date + timedelta(days=365):
				frappe.throw(
					_("Contract End Date must be at least one year after the Contract Start Date."),
					title=_("Invalid Contract Dates")
				)
		
		# Validate Shop status
		if self.shop:
			shop_doc = frappe.get_doc("Shop", self.shop) 
			if shop_doc.status == "Leased":
				frappe.throw(
					_("Shop {0} is already leased and cannot be contracted.").format(shop_doc.shop_name),
					title=_("Shop Leased")
				)

		self.make_payment_schedule()
		

	def on_submit(self):
		if self.shop:
			shop_doc = frappe.get_doc("Shop", self.shop)
			shop_doc.status = "Leased"
			shop_doc.tenant = self.tenant
			shop_doc.current_lease = self.name
			shop_doc.contract_expiry = self.contract_end
			shop_doc.save(ignore_permissions=True)
			frappe.msgprint(_("Shop {0} has been marked as 'Leased'.").format(shop_doc.shop_name), alert=True)

	def make_payment_schedule(self):
		self.payment_schedule = []

		if not self.contract_start or not self.contract_end or not self.payment_frequency:
			return

		# Convert to date objects if they are strings
		if isinstance(self.contract_start, str):
			start_date = datetime.strptime(self.contract_start, "%Y-%m-%d").date()
		else:
			start_date = self.contract_start

		if isinstance(self.contract_end, str):
			end_date = datetime.strptime(self.contract_end, "%Y-%m-%d").date()
		else:
			end_date = self.contract_end

		amount = self.rent_amount or frappe.db.get_single_value("Shop Settings", "default_rent_amount")
		freq = self.payment_frequency.lower()

		if freq == "monthly":
			step = relativedelta(months=1)
		elif freq == "quarterly":
			step = relativedelta(months=3)
		elif freq == "yearly":
			step = relativedelta(years=1)
		else:
			frappe.throw("Unsupported payment frequency: " + self.payment_frequency)

		current_date = start_date
		while current_date < end_date:
			self.append("payment_schedule", {
				"due_date": current_date,
				"rent_amount": amount,
				"status": "Pending"
			})
			current_date = current_date + step


@frappe.whitelist()
def send_rent_reminders():
	"""
	Sends email reminders to tenants 1 day before rent due date.
	"""
	enabled = frappe.db.get_single_value("Shop Settings", "enable_rent_reminders")
	if enabled:
		leases = frappe.get_all("Lease Contract",filters={},fields=["name", "tenant"])
		print(leases,'----------leases')
		for lease in leases:
			lease_doc = frappe.get_doc("Lease Contract", lease.name)
			print(lease_doc,'-------------lease doc')
			for row in lease_doc.payment_schedule:

				due_date = add_days(row.due_date, -1)
				today_date = datetime.strptime(today(), "%Y-%m-%d").date()
				print(due_date,'--------------------days')
				print(today_date,'-----------------today date')
				if row.status == "Pending" and due_date == today_date:
					print('if------------------')
					tenant_email = frappe.db.get_value("Tenant", lease_doc.tenant, "email")
					tenant_name = frappe.db.get_value("Tenant", lease_doc.tenant, "tenant_name")

					if not tenant_email:
						frappe.logger().warning(f"No email for tenant {lease_doc.tenant}")
						continue

					subject = f"Rent Payment Reminder - Due {row.due_date}"
					message = (
						f"Dear {tenant_name},\n\n"
						f"This is a friendly reminder that your rent of {row.rent_amount} for shop {lease_doc.shop} "
						f"is due on {row.due_date}.\n\n"
						f"Please ensure timely payment to avoid penalties.\n\n"
						f"Regards,\n"
						f"Airport Management"
					)


					try:
						frappe.sendmail(
							recipients=tenant_email,
							subject=subject,
							message=message,
							reference_doctype="Lease Contract",
							reference_name=lease_doc.name
						)
						frappe.logger().info(f"Sent rent reminder to {tenant_email} for Lease {lease_doc.name}")
					except Exception as e:
						frappe.log_error(message=str(e), title="Rent Reminder Email Failed")
