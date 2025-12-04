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
    ],
    "Company":[
        {
            "fieldname": "maintenance_accounts_section",
            "label": "Maintenance Accounts",
            "fieldtype": "Section Break",
            "insert_after": "default_deferred_expense_account",
            # "hide_border": 1
        },
        {
            "fieldname": "default_maintenance_expense_account",
            "label": "Default Maintenance Expense Account",
            "fieldtype": "Link",
            "options": "Account",
            "insert_after": "maintenance_accounts_section",
            # "description": "Used when Item-specific maintenance expense account is not set."
        },
        {
            "doctype": "Custom Field",
            "dt": "Company",
            "fieldname": "maintenance_accounts_column",
            "fieldtype": "Column Break",
            "insert_after": "default_maintenance_expense_account"
        },
        {
            "fieldname": "default_maintenance_cash_account",
            "label": "Default Maintenance Cash/Bank Account",
            "fieldtype": "Link",
            "options": "Account",
            "insert_after": "default_maintenance_expense_account",
            # "description": "Used when Item-specific cash/bank account is not configured."

        }
    ]
}

