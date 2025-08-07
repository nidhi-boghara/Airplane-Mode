# Copyright (c) 2025, Nidhi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import random
import string

class AirplaneTicket(Document):
	
	def before_save(self):
		add_ons_amount = 0
		for item in self.add_ons:
			add_ons_amount += item.amount

		self.total_amount = self.flight_price + add_ons_amount
	
	def validate(self):
		# Dictionary to keep track of unique add-ons
		unique_add_ons = {}
		removed_add_ons = []

		# Create a list of items to be removed
		items_to_remove = []

		# Iterate over the add_ons child table to find duplicates
		for add_on in self.add_ons:
			add_on_item = add_on.item 
			if add_on_item in unique_add_ons:
				# Duplicate found, add to the removal list
				removed_add_ons.append(add_on_item)
				items_to_remove.append(add_on)
			else:
				# Add the unique add-on to the dictionary
				unique_add_ons[add_on_item] = add_on.amount

		# Remove the duplicates after iteration
		for item in items_to_remove:
			self.remove(item)

		# If any duplicates found and removed give message to the user
		if removed_add_ons:
			frappe.msgprint(
				f"You can't have one add-on more then once. Removing: {', '.join(removed_add_ons)}",
				alert=True
			)
	
	def before_submit(self):
		if self.status != "Boarded":
			frappe.throw(f"The Airplane Ticket cannot be submitted because the status is '{self.status}'. Please ensure the status is 'Boarded' before submitting.")

	def before_insert(self):
		# Randomly assign the seat
		random_int = random.randint(1,99)
		random_char = random.choice('ABCDE')
		self.seat = f"{random_int}{random_char}"

		# Perform the validation in airline capacitty
		flight = self.flight
		airplane = frappe.get_doc("Airplane Flight", flight).airplane
		capacity = frappe.get_doc("Airplane", airplane).capacity
		total_tickets = frappe.db.count('Airplane Ticket', filters={'flight': flight})
		
		if total_tickets > capacity:
			frappe.throw(f"The number of tickets for {airplane} exceeds the airplane's capacity: {capacity}.")