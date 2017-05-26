##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Moulding',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base','product','sale','kg_sale_order','kg_weekly_plan','kg_daily_plan','kg_schedule'],
    'data': [
				'kg_moulding_view.xml',
				'sequence_data.xml'
			],
    'css': ['static/src/css/state.css'], 
    'auto_install': False,
    'installable': True,
}

