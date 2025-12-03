# Copyright (c) 2025, Task and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MachineMaintenance(Document):
    
	def validate(self):
		total = 0
		for row in self.parts_used:
			row.amount = flt(row.quantity) * flt(row.rate)
			total += row.amount
		self.cost = total