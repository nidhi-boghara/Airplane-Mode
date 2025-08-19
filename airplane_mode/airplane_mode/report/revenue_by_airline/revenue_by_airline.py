# Copyright (c) 2025, Nidhi and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	chart = get_chart_data(data)
	total_revenue = sum(row[1] for row in data)

	summary = [
		{'label': 'Total Revenue', 'value':total_revenue}
	]

	return columns, data, None, chart, summary

def get_columns():
	return [
		{
			"fieldname" : "airline",
			"label" : "Airline",
			"fieldtype" : "Link",
			"options" : "Airline",
			"width" : "110"
		},
		{
			"fieldname" : "revenue",
			"label" : "Revenue",
			"fieldtype" : "Currency",
			"width" : "110"
		}
	]

def get_data():
    data = []
    
    airlines = frappe.get_all("Airline", fields=["name"])
    for airline in airlines:
        total_revenue = 0.0

        airplanes = frappe.get_all("Airplane",filters={"airline": airline.name},pluck="name")

        if not airplanes:
            data.append([airline.name, 0.0])
            continue

        flights = frappe.get_all("Airplane Flight",filters={"airplane": ["in", airplanes]},pluck="name")

        if not flights:
            data.append([airline.name, 0.0])
            continue

        tickets = frappe.get_all("Airplane Ticket",filters={"flight": ["in", flights]},fields=["name", "flight_price"])

        for ticket in tickets:
            ticket_revenue = ticket.flight_price or 0.0

            addons = frappe.get_all("Airplane Ticket Add-on Item",filters={"parent": ticket.name},pluck="amount")

            ticket_revenue += sum(addons) if addons else 0.0
            total_revenue += ticket_revenue

        data.append([airline.name, total_revenue])

    return data


def get_chart_data(data):
	labels = [row[0] for row in data]  # Airline names
	values = [row[1] for row in data]  # Revenue values

	chart = {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": "Revenue",
					"values": values
				}
			]
		},
		"type": "donut"
	}
	return chart

