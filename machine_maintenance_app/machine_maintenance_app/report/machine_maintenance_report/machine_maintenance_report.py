# Copyright (c) 2025, Task and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import getdate

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	return [
		{"label": "Machine", "fieldname": "machine", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": "Maintenance Date", "fieldname": "maintenance_date", "fieldtype": "Date", "width": 120},
		{"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "Employee", "width": 180},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": "Total Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 140},
	]

def get_data(filters):
	consolidated = filters.get("consolidated")
	conditions = "1=1"

	if filters.get("machine"):
		conditions += f" AND machine_name = '{filters.machine}'"

	if filters.get("technician"):
		conditions += f" AND technician = '{filters.technician}'"

	if filters.get("from_date"):
		conditions += f" AND maintenance_date >= '{filters.from_date}'"

	if filters.get("to_date"):
		conditions += f" AND maintenance_date <= '{filters.to_date}'"

	query = f"""
		SELECT
			machine_name AS machine,
			maintenance_date,
			technician,
			status,
			cost
		FROM
			`tabMachine Maintenance`
		WHERE {conditions}
	"""

	records = frappe.db.sql(query, as_dict=True)
	
	if consolidated:
		grouped = {}
		for row in records:
			if row.machine not in grouped:
				grouped[row.machine] = {
					"machine": row.machine,
					"maintenance_date": "", 
					"technician": "",
					"status": "Consolidated",
					"cost": 0
				}
			grouped[row.machine]["cost"] += row.cost

		return list(grouped.values())

	return records
