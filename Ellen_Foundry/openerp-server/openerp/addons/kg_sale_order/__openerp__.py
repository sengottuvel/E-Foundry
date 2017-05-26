##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Kg Sale Order',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base', 'sale','product','kg_product'],
    'data': [
		'kg_sale_order_view.xml',
		],
    'css': ['static/src/css/state.css'], 		
    'auto_install': False,
    'installable': True,
}

