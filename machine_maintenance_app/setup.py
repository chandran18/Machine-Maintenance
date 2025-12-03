import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.exceptions import ValidationError
from machine_maintenance_app.machine_maintenance_app.doctype.custom.custom_fields import CUSTOM_FIELDS


def setup_fixtures():
    print("New")
    filtered_fields = {}

    for doctype, fields in CUSTOM_FIELDS.items():
        for field in fields:
            fieldname = field.get("fieldname")
            print("sssssssssssssssssssssssss",fieldname)

            if frappe.db.exists("Custom Field", f"{doctype}-{fieldname}"):
                continue

            filtered_fields.setdefault(doctype, []).append(field)

    for doctype, fields in filtered_fields.items():
        for field in fields:
            try:
                create_custom_fields({doctype: [field]})
            except ValidationError:
                continue

def remove_custom_fields():
    # Loop through your custom field structure
    for doctype, fields in CUSTOM_FIELDS.items():
        for field in fields:
            fieldname = field.get("fieldname")

            # Get ALL matching Custom Field records
            custom_fields = frappe.get_all(
                "Custom Field",
                filters={"dt": doctype, "fieldname": fieldname},
                pluck="name"
            )

            if not custom_fields:
                print(f"No Custom Field found for {doctype} - {fieldname}")
                continue

            # Delete all matching custom fields
            for cf in custom_fields:
                try:
                    frappe.delete_doc("Custom Field", cf, force=True)
                    print(f"Deleted: {cf}")
                except Exception as e:
                    print(f"Error deleting {cf}: {e}")

        # Clear cache for this DocType after all deletions
        frappe.clear_cache(doctype=doctype)

    # Commit changes to DB
    frappe.db.commit()
    print("Custom Field Cleanup Complete!")




