// Copyright (c) 2025, Nidhi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shop", {
    setup: function(frm) {
        frm.set_query('shop_type', function() {
            return {
                filters: {
                    "enabled": 1
                }
            };
        });
        if (!frm.doc.default_rent) {
            frappe.call({
                method: 'frappe.client.get',
                args: { doctype: 'Shop Settings', name: 'Shop Settings' },
                callback: function(r) {
                    if (r.message && r.message.default_rent_amount) {
                        frm.set_value('default_rent', r.message.default_rent_amount);
                    }
                }
            })
        }
    }
});
