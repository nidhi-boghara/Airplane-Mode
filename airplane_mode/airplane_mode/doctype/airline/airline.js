// Copyright (c) 2025, Nidhi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airline", {
    refresh(frm) {
        if(frm.doc.website) {
            // Web Link
            frm.add_web_link('Visit Website', frm.doc.website);
        }
    }
});