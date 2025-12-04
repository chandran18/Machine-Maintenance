// Copyright (c) 2025, Task and contributors
// For license information, please see license.txt

frappe.query_reports["Machine Maintenance Report"] = {
    "filters": [
        {
            "fieldname": "machine",
            "label": "Machine",
            "fieldtype": "Link",
            "options": "Item",
			"get_query": function() {
                return {
                    "filters": {
                        "is_machine": 1      // only machines
                    }
                };
            }
        },
        {
            "fieldname": "technician",
            "label": "Technician",
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "consolidated",
            "label": "Consolidated",
            "fieldtype": "Check",
            "default": 0
        },
    ],

    formatter: function(value, row, column, data, default_formatter) {
        let formatted = default_formatter(value, row, column, data);

        if (!data) return formatted;

        // COLORS:
        if (data.status === "Overdue") {
            formatted = `<span style="background-color:#FFCCCC; padding:3px; border-radius:3px;"> ${value} </span>`;
        }
        if (data.status === "Scheduled") {
            formatted = `<span style="background-color:#FFF5CC; padding:3px; border-radius:3px;"> ${value} </span>`;
        }
        if (data.status === "Completed") {
            formatted = `<span style="background-color:#D6F5D6; padding:3px; border-radius:3px;"> ${value} </span>`;
        }

        return formatted;
    }
};
