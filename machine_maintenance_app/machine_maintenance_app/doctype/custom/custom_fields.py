import frappe

CUSTOM_FIELDS = {
    "Item": [
        {
            "fieldname": "is_machine",
            "label": "Is Machine",
            "fieldtype": "Check",
            "insert_after": "is_stock_item",
            "description": "Enable if this Item is a machine or equipment that requires maintenance."
        },
        {
            "fieldname": "machine_maintenance_section",
            "label": "Machine Maintenance",
            "fieldtype": "Section Break",
            "insert_after": "enable_deferred_revenue",
            "collapsible": 1
        },
        {
            "fieldname": "machine_maintenance_accounts",
            "label": "Machine Maintenance Accounts",
            "fieldtype": "Table",
            "options": "Machine Maintenance Accounting",
            "insert_after": "machine_maintenance_section",
            "description": "Company-wise maintenance accounting configuration."
        }
    ]
}

