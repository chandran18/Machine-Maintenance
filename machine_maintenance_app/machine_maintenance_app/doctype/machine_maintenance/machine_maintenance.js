// Copyright (c) 2025, Task and contributors
// For license information, please see license.txt
frappe.ui.form.on("Machine Maintenance", {
	onload:function(frm) {
        if (frm.is_new()){
            frm.set_value('maintenance_date',frappe.datetime.get_today());
        }
        toggle_notes_visibility(frm);
        toggle_account_fields(frm);
        fetch_accounts(frm);
	},
    refresh: function(frm){
        toggle_notes_visibility(frm);
        toggle_account_fields(frm);
        set_overdue_if_needed(frm);
        fetch_accounts(frm);
        show_overdue_badge(frm);


        filter_machine(frm);
        if (!frm.is_new() && frm.doc.docstatus !== 1 && frm.doc.status !== 'Completed'){
            frm.add_custom_button(__('Mark Completed'), ()=>{
                frappe.confirm(__('Mark this maintenance as Completed?'),
                () =>{
                    frappe.call({
                        method: 'machine_maintenance_app.machine_maintenance_app.doctype.machine_maintenance.machine_maintenance.mark_completed',
                        args:{ name: frm.doc.name },
                        // freeze:true,
                        callback:function(r){
                            if(!r.exc){
                                frappe.show_alert({message: __('Marked Completed'), indicator: 'green'});
                                frm.reload_doc();
                            }
                        }
                    });
                }
              )
            })
        }
    },

    maintenance_date: function(frm){
        set_overdue_if_needed(frm);
    },
    status: function(frm){
        toggle_notes_visibility(frm);
    },
    machine_name(frm) {
        if (!frm.doc.company) {
            frappe.msgprint("Please select a Company before selecting the Machine.");
            frm.set_value("machine_name", "");
            return;
        }
        fetch_accounts(frm);
    },
    company(frm) {
        // Clear existing accounts whenever company changes
        frm.set_value("expense_account", "");
        frm.set_value("cash_bank_account", "");
        toggle_account_fields(frm);

        if (frm.doc.machine_name) {
            fetch_accounts(frm);
        }
    },
    setup(frm) {
        frm.set_query("part", "parts_used", function(doc, cdt, cdn) {
            return {
                filters: {
                    is_machine: 0 
                }
            };
        });
    }

});
frappe.ui.form.on('Parts Used',{
    quantity: function(frm, cdt, cdn){
        calculate_part_amount(frm, cdt, cdn);
    },
    rate: function(frm,cdt,cdn){
        calculate_part_amount(frm,cdt,cdn);
    },
});

function calculate_part_amount(frm,cdt,cdn){
    let row = locals[cdt][cdn];
    let qty = flt(row.quantity);
    let rate = flt(row.rate);
    let amount = flt(qty*rate);
    frappe.model.set_value(cdt,cdn,"amount",amount);
}

function toggle_notes_visibility(frm) {
    if (frm.doc.status === 'Scheduled' || frm.doc.status === '') {
        frm.toggle_display('notes', false);
    } else {
        frm.toggle_display('notes', true);
    }
}

function toggle_account_fields(frm) {
    const fields = ["expense_account", "cash_bank_account"];

    if (frm.doc.company) {
        fields.forEach(f => frm.toggle_display(f, true));
    } else {
        fields.forEach(f => frm.toggle_display(f, false));
    }
}


function set_overdue_if_needed(frm) {
    if (!frm.doc.maintenance_date || frm.doc.status === 'Completed') return;
    const today = frappe.datetime.get_today();
    try {
        if (frappe.datetime.str_to_obj(frm.doc.maintenance_date) < frappe.datetime.str_to_obj(today)) {
            if (frm.doc.status !== 'Overdue') {
                frm.set_value('status', 'Overdue');
            }
        }
    } catch (e) {
    }
}

function filter_machine(frm){
    frm.set_query('machine_name', function(){
        return{
            filters:{
                is_machine:true
            }
        }
    })
}

function fetch_accounts(frm) {
    frappe.call({
        method: "machine_maintenance_app.machine_maintenance_app.doctype.machine_maintenance.machine_maintenance.get_accounts",
        args: {
            machine: frm.doc.machine_name,
            company: frm.doc.company
        },
        callback(r) {
            if (r.message) {
                frm.set_value("expense_account", r.message.expense_account);
                frm.set_value("cash_bank_account", r.message.cash_bank_account);
            }
        }
    });
}

function show_overdue_badge(frm) {
    if (!frm.doc.maintenance_date) return;

    const today = frappe.datetime.get_today();
    const md = frappe.datetime.str_to_obj(frm.doc.maintenance_date);

    if (md < frappe.datetime.str_to_obj(today)
        && frm.doc.workflow_state !== "Completed"
        && frm.doc.workflow_state !== "Closed") {

        frm.dashboard.set_headline(
            __("⚠ This maintenance task is OVERDUE"),
            "red"
        );
    }
}
