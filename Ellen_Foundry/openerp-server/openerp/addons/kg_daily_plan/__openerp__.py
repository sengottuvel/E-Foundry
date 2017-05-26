##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Daily Plan',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base','product','sale','kg_sale_order','kg_weekly_plan','kg_metal_grade_master','kg_schedule'],
    'data': [
				'kg_daily_plan_view.xml',
				'sequence_data.xml'
			],
    'css': ['static/src/css/state.css'], 
    'auto_install': False,
    'installable': True,
}

