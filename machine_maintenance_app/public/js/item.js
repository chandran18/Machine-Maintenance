frappe.ui.form.on("Item", {
    setup: function(frm) {
        frm.fields_dict["machine_maintenance_accounts"].grid.get_field("maintenance_expense_account").get_query =
            function(doc, cdt, cdn) {
                let row = locals[cdt][cdn];
                return {
                    filters: {
                        company: row.company,
                        root_type: "Expense",
                        is_group: 0
                    }
                };
            };

        frm.fields_dict["machine_maintenance_accounts"].grid.get_field("cashbank_account").get_query =
            function(doc, cdt, cdn) {
                let row = locals[cdt][cdn];
                return {
                    filters: {
                        company: row.company,
                        account_type: ["in", ["Cash", "Bank"]],
                        is_group: 0
                    }
                };
            };
    }
});
