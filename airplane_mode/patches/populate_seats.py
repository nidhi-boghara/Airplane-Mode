import frappe
import random

def execute():
    airplane_tickets = frappe.get_all("Airplane Ticket",filters={'seat':None},fields=[])
    for ticket in airplane_tickets:
        ticket_doc = frappe.get_doc("Airplane Ticket",ticket.name)
        random_int = random.randint(1,99)
        random_char = random.choice('ABCDE')
        ticket_doc.seat = f"{random_int}{random_char}"
        ticket_doc.save()