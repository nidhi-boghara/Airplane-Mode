# Copyright (c) 2025, Nidhi and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _

class Shop(WebsiteGenerator):
	
	def before_save(self):
		if self.status == "Available":
			self.tenant = None
			self.tenant_name = None
			self.contract_expiry = None
			frappe.msgprint(_("Tenant details and contract expiry have been cleared because the shop is now available."), alert=True)