##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

##############################################################################
{
    'name': 'KG_Purchase_Order',
    'version': '0.1',
    'author': 'sengottuvel',
    'category': 'KG_Purchase_Order',
    'website': 'http://www.openerp.com',
    'description': """
This module allows you to manage your Purchase Requisition.
===========================================================

When a purchase order is created, you now have the opportunity to save the
related requisition. This new object will regroup and will allow you to easily
keep track and order all your purchase orders.
""",
    'depends' : ['base', 'product', 'purchase','purchase_requisition','kg_purchase_indent','kg_expense_master'],
    'data': ['kg_purchase_order_view.xml','jasper_report.xml',
			
			],
	'test': [
        'test/ui/print_report.yml',
          ],
    #'css': ['static/src/css/state.css'],
    'auto_install': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

