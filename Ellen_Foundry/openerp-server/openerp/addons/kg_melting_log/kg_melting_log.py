from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import math
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')

class kg_melting_log(osv.osv):

	_name = "kg.melting.log"
	_description = "Melting Log"
	_order = "entry_date desc"
	_rec_name = "furnance_heat_no"
	
	_columns = {
	
		## Version 0.1
		
		## Basic Info	
		
		'name': fields.char('Melt No' ,select=True,readonly=True),
		'entry_date':fields.date('Melt Date',required=True),
		'remark': fields.text('Remarks'),	
		'note': fields.text('Notes'),	
		'state': fields.selection([('draft','Draft'),('confirmed','WFA'),('approved','Approved'),('cancel','Cancelled')],'Status', readonly=True),
		'entry_mode': fields.selection([('auto','Auto'),('manual','Manual')],'Entry Mode', readonly=True),

		## Entry Info
		
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),	
		'active': fields.boolean('Active'),
		'crt_date': fields.datetime('Created Date',readonly=True),
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),		
		'confirm_date': fields.datetime('Confirmed Date', readonly=True),
		'confirm_user_id': fields.many2one('res.users', 'Confirmed By', readonly=True),		
		'ap_rej_date': fields.datetime('Approved/Rejected Date', readonly=True),
		'ap_rej_user_id': fields.many2one('res.users', 'Approved/Rejected By', readonly=True),	
		'cancel_date': fields.datetime('Cancelled Date', readonly=True),
		'cancel_user_id': fields.many2one('res.users', 'Cancelled By', readonly=True),
		'update_date': fields.datetime('Last Updated Date', readonly=True),
		'update_user_id': fields.many2one('res.users', 'Last Updated By', readonly=True),		
		
		
		## Module Requirement Info
		
		'furnance_heat_no':fields.char('Furnance Heat No',required=True),
		'grade_id':fields.many2one('kg.metal.grade.master','Grade ',required=True,domain=[('state','=','approved')]),
		'tapping_temp':fields.char('Tapping Temp',required=True),
		'pouring_temp':fields.char('Pouring Temp',required=True),
		'tapping_opt':fields.char('Tapping Opt'),
		'pouring_opt':fields.char('Pouring Opt'),
		'silicon':fields.char('Silicon'),
		'copper':fields.char('Copper'),
		'magnesium':fields.char('Magnesium'),
		'shell_coke':fields.float('Shell Coke'),
		'pet_coke':fields.float('Pet Coke'),
		'fesi':fields.float('Fesi'),
		'femn':fields.float('Femn'),
		'cu':fields.float('Cu'),
		'fesi_mg':fields.float('Fesi Mg'),
		'inoculant':fields.float('Inoculant'),
		'sg_pig_iron':fields.float('SG Pig Iron'),
		'returns':fields.float('Returns'),
		'mild_steel':fields.float('Mild Steel'),
		'ci_boring':fields.float('CI Boring'),
		'pig_iron':fields.float('Pig Iron'),
		'silicon_steel':fields.float('Silicon Steel'),
		'spillage':fields.float('Spillage'),
		'ci_scrap':fields.float('CI Scrap'),
		'base_metal':fields.float('Base Metal'),
		'total':fields.float('Total'),
		'initial_reading':fields.float('Initial Reading'),
		'final_reading':fields.float('Final Reading'),
		'units_heat':fields.float('Units/Heat'),
		'units_ton':fields.float('Units/Ton'),
		'furnace_started':fields.float('Furnace Started'),
		'pouring_started':fields.float('Pouring Started'),
		'pouring_finished':fields.float('Pouring Finished'),
		'during_time':fields.float('During Time'),
		
		
		## Child Tables Declaration
				

	}
	

	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg_melting', context=c),			
		'entry_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'state': 'draft',		
		'active': True,
		'entry_mode': 'manual',
	
	}
		
				
		
	def entry_confirm(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])

		### Sequence Number Generation  ###

		if rec.state == 'draft':		
			if rec.name == '' or rec.name == False:
				seq_obj_id = self.pool.get('ir.sequence').search(cr,uid,[('code','=','kg.melting.log')])
				seq_rec = self.pool.get('ir.sequence').browse(cr,uid,seq_obj_id[0])
				cr.execute("""select generatesequenceno(%s,'%s','%s') """%(seq_obj_id[0],seq_rec.code,rec.entry_date))
				entry_name = cr.fetchone();
				entry_name = entry_name[0]	
			else:
				entry_name = rec.name	
			self.write(cr, uid, ids, {'name':entry_name,'state': 'confirmed','confirm_user_id': uid, 'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
		return True						


	def entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'confirmed':	
			self.write(cr, uid, ids, {'state': 'approved','ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
		return True			
		

		
	def unlink(self,cr,uid,ids,context=None):
		unlink_ids = []		
		for rec in self.browse(cr,uid,ids):	
			if rec.state != 'draft':			
				raise osv.except_osv(_('Warning!'),
						_('You can not delete this entry !!'))
			else:
				unlink_ids.append(rec.id)
		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)	
			
			
	def create(self, cr, uid, vals, context=None):
		return super(kg_melting_log, self).create(cr, uid, vals, context=context)
		
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_melting_log, self).write(cr, uid, ids, vals, context)		
		
				
	_sql_constraints = [
	
		('name', 'unique(name)', 'No must be Unique !!'),
		('furnance_heat_no', 'unique(furnance_heat_no)', 'Furnance Heat No must be Unique !!'),
	]					
	

kg_melting_log()


	
