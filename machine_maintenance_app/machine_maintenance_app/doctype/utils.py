import frappe
from frappe.utils import getdate, nowdate

def mark_overdue_maintenance():
    today = nowdate()
    rows = frappe.db.get_all('Machine Maintenance', filters={'maintenance_date': ['<', today], 'status': ['!=', 'Completed'], 'docstatus': 0}, fields=['name'])
    for r in rows:
        doc = frappe.get_doc('Machine Maintenance', r.name)
        doc.status = 'Overdue'
        doc.save()
        # notify
        frappe.enqueue('machine_maintenance_app.machine_maintenance_app.doctype.machine_maintenance.machine_maintenance.send_maintenance_overdue_email', doc=doc)
