##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Schedule',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base','product','kg_production_unit','sale','kg_sale_order'],
    'data': [
				'kg_schedule_view.xml',
				'sequence_data.xml'
			],
    'css': ['static/src/css/state.css'], 
    'auto_install': False,
    'installable': True,
}

