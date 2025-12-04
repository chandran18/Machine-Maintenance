# Copyright (c) 2025, Task and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils import nowdate,getdate
from frappe.model.workflow import apply_workflow
from erpnext.setup.utils import get_exchange_rate


class MachineMaintenance(Document):
	
	def validate(self):
		self.compute_parts_amounts()
		self.validate_dates()
		self.validate_cost_non_negative()

	def before_submit(self):
		"""Extra checks before submission (if required)."""
		if not self.technician:
			frappe.throw(("Technician must be assigned before submission"))

	def on_submit(self):
		"""On submit: create Journal Entry (if cost > 0) and send notifications if needed."""
		if flt(self.cost) > 0:
			create_maintenance_journal_entry(self)
		if self.status == "Completed":
			send_maintenance_completed_email(self)

	def on_update(self):
		"""Triggered on any save/update. Use to send scheduled/overdue emails."""
		previous_status = frappe.db.get_value("Machine Maintenance", self.name, "status")
		if previous_status and previous_status != self.status:
			if self.status == "Scheduled":
				send_maintenance_scheduled_email(self)
			elif self.status == "Overdue":
				send_maintenance_overdue_email(self)
			elif self.status == "Completed":
				send_maintenance_completed_email(self)


	def compute_parts_amounts(self):
		total = 0
		for row in self.parts_used:
			row.amount = flt(row.quantity) * flt(row.rate)
			total += row.amount
		self.cost = total

	def validate_dates(self):
		if self.completion_date and self.maintenance_date:
			if getdate(self.completion_date) < getdate(self.maintenance_date):
				frappe.throw(("Completion date cannot be before Maintenance date"))

	def validate_cost_non_negative(self):
		if flt(self.cost) < 0:
			frappe.throw(("Cost cannot be negative"))


def get_ops_manager_emails():
	"""Return a list of emails for users with role 'Operations Manager'. Falls back to maintenance settings email."""
	emails = []
	for r in frappe.get_all("Has Role", filters={"role": "Operations Manager"}, fields=["parent"]):
		email = frappe.get_value("User", r.parent, "email")
		if email:
			emails.append(email)
	# # fallback to Maintenance Settings if available
	# if not emails and frappe.db.exists("DocType", "Maintenance Settings"):
	# 	try:
	# 		ms = frappe.get_single("Maintenance Settings")
	# 		if ms.operations_manager_email:
	# 			emails = [ms.operations_manager_email]
	# 	except Exception:
	# 		pass
	# return list(set(emails))


def send_maintenance_completed_email(doc):
	recipients = get_ops_manager_emails()
	if not recipients:
		return
	subject = _("Maintenance Completed: {0}").format(doc.name)
	message = _("Maintenance for {0} completed on {1}. Total Cost: {2}").format(doc.machine_name, doc.completion_date or nowdate(), doc.cost)
	frappe.sendmail(recipients=recipients, subject=subject, message=message)

def send_maintenance_scheduled_email(doc):
	recipients = get_ops_manager_emails()
	if not recipients:
		return
	subject = _("Maintenance Scheduled: {0}").format(doc.name)
	message = _("Maintenance for {0} scheduled on {1}.").format(doc.machine_name, doc.maintenance_date)
	frappe.sendmail(recipients=recipients, subject=subject, message=message)

def send_maintenance_overdue_email(doc):
	recipients = get_ops_manager_emails()
	if not recipients:
		return
	subject = _("Maintenance Overdue: {0}").format(doc.name)
	message = _("Maintenance for {0} scheduled on {1} is now overdue.").format(doc.machine_name, doc.maintenance_date)
	frappe.sendmail(recipients=recipients, subject=subject, message=message)
	

@frappe.whitelist()
def mark_completed(name):
	doc = frappe.get_doc("Machine Maintenance", name)

	try:
		apply_workflow(doc, "Complete")
	except Exception as e:
		frappe.throw(f"Workflow action failed: {e}")

	doc.status = "Completed"

	if not doc.completion_date:
		doc.completion_date = nowdate()

	doc.save()
	return {"status": "ok", "name": doc.name}




@frappe.whitelist()
def get_accounts(machine=None, company=None):

	if not company:
		return {}

	if not machine:
		comp = frappe.get_doc("Company", company)
		return {
			"expense_account": comp.default_maintenance_expense_account,
			"cash_bank_account": comp.default_maintenance_cash_account
		}

	item = frappe.get_doc("Item", machine)

	for row in (item.machine_maintenance_accounts or []):
		if row.company == company:
			return {
				"expense_account": row.expense_account,
				"cash_bank_account": row.cash_bank_account
			}

	comp = frappe.get_doc("Company", company)
	return {
		"expense_account": comp.default_maintenance_expense_account,
		"cash_bank_account": comp.default_maintenance_cash_account
	}


def create_maintenance_journal_entry(self):
	"""
	Create Journal Entry for Machine Maintenance with multi-currency support.
	Debit: Expense Account
	Credit: Cash/Bank Account
	Party: Technician (Employee)
	"""
	if not self.expense_account:
		frappe.throw("Please set the Maintenance Expense Account.")

	if not self.cash_bank_account:
		frappe.throw("Please set the Cash/Bank Account.")

	if not self.technician:
		frappe.throw("Technician is required to create Journal Entry.")

	if flt(self.cost) <= 0:
		frappe.throw("Cost must be greater than zero.")

	amount = flt(self.cost)

	company_currency = frappe.get_value("Company", self.company, "default_currency")

	expense_currency = frappe.get_value("Account", self.expense_account, "account_currency") or company_currency
	cash_currency = frappe.get_value("Account", self.cash_bank_account, "account_currency") or company_currency


	def get_rate(from_currency, to_currency):
		if from_currency == to_currency:
			return 1
		return get_exchange_rate(from_currency, to_currency)

	expense_rate = get_rate(expense_currency, company_currency)
	cash_rate = get_rate(cash_currency, company_currency)

	expense_base_amount = amount * expense_rate
	cash_base_amount = expense_base_amount * cash_rate
	print("cash_base_amount",cash_base_amount)

	je = frappe.new_doc("Journal Entry")
	je.company = self.company
	je.voucher_type = "Journal Entry"
	je.posting_date = self.maintenance_date or nowdate()
	je.multi_currency = 1
	je.user_remark = f"Machine Maintenance: {self.machine_name}"

	je.append("accounts", {
		"account": self.expense_account,
		"debit_in_account_currency": amount,
		"exchange_rate": expense_rate,
		"debit": expense_base_amount,
	})

	je.append("accounts", {
		"account": self.cash_bank_account,
		"credit_in_account_currency": expense_base_amount,
		"exchange_rate": cash_rate,
		"credit": cash_base_amount,
		"party_type": "Employee",
		"party": self.technician,
	})


	je.insert(ignore_permissions=True)
	je.submit()

	self.db_set("journal_entry", je.name)

	frappe.msgprint(f"Journal Entry <b>{je.name}</b> created successfully.")
