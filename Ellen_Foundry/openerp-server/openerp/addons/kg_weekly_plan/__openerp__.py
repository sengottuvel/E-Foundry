##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Weekly Plan',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base','product','kg_metal_grade_master','kg_schedule'],
    'data': [
				'kg_weekly_plan_view.xml',
				'sequence_data.xml'
			],
    'css': ['static/src/css/state.css'], 
    'auto_install': False,
    'installable': True,
}

