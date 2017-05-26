##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Re-shot Blasting',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base','product','sale','kg_sale_order','kg_painting_process','kg_first_inspection','kg_weekly_plan','kg_daily_plan','kg_schedule','kg_metal_grade_master','kg_production_unit','kg_moulding','kg_melting','kg_final_inspection'],
    'data': [
				'kg_reshot_blasting_view.xml',
				'sequence_data.xml'
			],
    'css': ['static/src/css/state.css'], 
    'auto_install': False,
    'installable': True,
}

