##############################################################################
#
#   Standard Transaction Module
#
##############################################################################

{
    'name': 'Melting Log',
    'version': '0.1',
    'author': 'dinesh',
    'depends' : ['base','kg_metal_grade_master'],
    'data': [
				'kg_melting_log_view.xml',
				'sequence_data.xml'
			],
    'css': ['static/src/css/state.css'], 
    'auto_install': False,
    'installable': True,
}

