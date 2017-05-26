from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from datetime import datetime
import re
import math
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kg_metal_grade_master(osv.osv):

	_name = "kg.metal.grade.master"
	_description = "Metal Grade Master"
	
	### Version 0.1
	
	def _get_modify(self, cr, uid, ids, field_name, arg,  context=None):
		res={}
		if field_name == 'modify':
			for h in self.browse(cr, uid, ids, context=None):
				res[h.id] = 'no'
				if h.state == 'approved':
					cr.execute(""" select * from 
					(SELECT tc.table_schema, tc.constraint_name, tc.table_name, kcu.column_name, ccu.table_name
					AS foreign_table_name, ccu.column_name AS foreign_column_name
					FROM information_schema.table_constraints tc
					JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
					JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
					WHERE constraint_type = 'FOREIGN KEY'
					AND ccu.table_name='%s')
					as sam  """ %('kg_metal_grade_master'))
					data = cr.dictfetchall()	
					if data:
						for var in data:
							data = var
							chk_sql = 'Select COALESCE(count(*),0) as cnt from '+str(data['table_name'])+' where '+data['column_name']+' = '+str(ids[0])
							cr.execute(chk_sql)			
							out_data = cr.dictfetchone()
							if out_data:
								if out_data['cnt'] > 0:
									res[h.id] = 'no'
									return res
								else:
									res[h.id] = 'yes'
					else:
						res[h.id] = 'yes'
				else:
					res[h.id] = 'no'									
		return res		
		
		### Version 0.2		

	_columns = {
	
		## Basic Info	
		
		'name': fields.char('Name', size=128, required=True),
		'code':fields.char('Code',size=4),
		'state': fields.selection([('draft','Draft'),('confirm','WFA'),('approved','Approved'),
				('reject','Rejected'),('cancel','Cancelled')],'Status', readonly=True),
		'notes': fields.text('Notes'),	
		'remark': fields.text('Remarks'),
		'cancel_remark': fields.text('Cancel Remarks'),			
		'modify': fields.function(_get_modify, string='Modify', method=True, type='char', size=3),
		'entry_mode': fields.selection([('auto','Auto'),('manual','Manual')],'Entry Mode', readonly=True),
		
		## Entry Info
		
		'active': fields.boolean('Active'),
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'crt_date':fields.datetime('Created Date',readonly=True),
		'confirm_date': fields.datetime('Confirmed Date', readonly=True),
		'confirm_user_id': fields.many2one('res.users', 'Confirmed By', readonly=True),
		'ap_rej_date': fields.datetime('Approved/Rejected Date', readonly=True),
		'ap_rej_user_id': fields.many2one('res.users', 'Approved/Rejected By', readonly=True),
		'cancel_user_id': fields.many2one('res.users', 'Cancelled By', readonly=True),
		'cancel_date': fields.datetime('Cancelled Date', readonly=True),
		'update_date': fields.datetime('Last Updated Date',readonly=True),
		'update_user_id': fields.many2one('res.users','Last Updated By',readonly=True),		
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),
		
		## Module Requirement Info

		'sg_pig_iron':fields.float('SG Pig Iron(kgs)',required=True),
		'sg_pig_iron_max':fields.float('SG Pig Iron1(kgs)',required=True),
		'scrap':fields.float('Scrap(kgs)',required=True),
		'scrap_max':fields.float('Scrap(kgs)',required=True),		
		'boring':fields.float('Borings(kgs)',required=True),
		'boring_max':fields.float('Borings(kgs)',required=True),
		'returns':fields.float('Returns(kgs)',required=True),
		'returns_max':fields.float('Returns(kgs)1',required=True),
		'ms_scrap':fields.float('M S Scrap(Kgs)',required=True),
		'ms_scrap_max':fields.float('M.S.Scrap',required=True),
		'silicon_steel':fields.float('Silicon Steel(Kgs)',required=True),
		'silicon_steel_max':fields.float('Silicon Steel',required=True),
		'carbon':fields.float('Carbon(%)',required=True),
		'carbon_max':fields.float('Carbon1',required=True),
		'silicon':fields.float('Silicon(%)',required=True),
		'silicon_max':fields.float('Silicon1 ',required=True),
		'magnanese':fields.float('Magnanese(%)',required=True),
		'magnanese_max':fields.float('Magnanese1',required=True),
		'phosphorous':fields.float('Phosphorous(%)',required=True),
		'phosphorous_min_max':fields.float('Phosphorous1',required=True),
		'sulphur':fields.float('Sulphur(%)',required=True),
		'sulphur_max':fields.float('Sulphur1',required=True),
		'copper':fields.float('Copper(%)',required=True),
		'copper_max':fields.float('Copper1',required=True),
		'fe_si_mg_percent':fields.float('Fe.Si Mg Percentage(%)',required=True),
		'inoculation':fields.float('Inoculation(%)',required=True),
		'inoculation_max':fields.float('Inoculation1',required=True),
		'tapping_temp':fields.float('Tapping Temperature(%)',required=True),
		'tapping_temp_max':fields.float('Tapping Temperature1',required=True),
		'pouring_temp':fields.float('Pouring Temperature(%)',required=True),
		'pouring_temp_max':fields.float('Pouring Temperature1',required=True),
		'pouring_time':fields.float('Pouring Time',required=True),
		'pouring_time_max':fields.float('Pouring Time1',required=True),
		'cooling_time':fields.float('Cooling time(Mins)',required=True),
		'cooling_time_max':fields.float('Cooling time(Mins)1',required=True),
		'magnesium':fields.float('Magnesium(%)',required=True),
		'magnesium_max':fields.float('Magnesium1',required=True),
		'sand_process':fields.selection([('unitsand','Unit Sand'),('a','A'),('b','B')],'Sand Process'),
		'carbon_percent':fields.float('Carbon(%)'),
		'carbon_percent_max':fields.float('Carbon1 %'),
		'silicon_percent':fields.float('Silicon(%)'),
		'silicon_percent_max':fields.float('Silicon1 %'),
		'manganese_percent':fields.float('Manganese(%)'),
		'manganese_percent_max':fields.float('Manganee %'),
		'sulphur_percent':fields.float('Sulphur(%)'),
		'sulphur_percent_max':fields.float('Sulphur1 %'),
		'copper_percent':fields.float('Copper(%)'),
		'copper_percent_max':fields.float('Copper1 %'),
		'magnesium_percent':fields.float('Magnesium(%)'),
		'magnesium_percent_max':fields.float('Magnesium1 %'),
		'tensile_str':fields.float('Tensile Strength(N/mm^2)'),
		'tensile_str_max':fields.float('Tensile Strength1(N/mm^2)'),
		'yield_str':fields.float('Yield Strength(N/mm^2)'),
		'yield_str_max':fields.float('Yield Strength1(N/mm^2)'),
		'elongation_percent':fields.float('Elongation(%)'),
		'elongation_percent_max':fields.float('Elongation1 %'),
		'bhn':fields.float('BHN '),
		'bhn_max':fields.float('BHN1 '),
		'nodularity_percent':fields.float('Nodularity(%)'),
		'nodularity_percent_max':fields.float('Nodularity1 %'),
		'pearlite_percent':fields.float('Pearlite(%)'),
		'pearlite_percent_max':fields.float('Pearlite1%'),
		'ferrite_percent':fields.float('Ferrite(%)'),
		'ferrite_percent_max':fields.float('Ferrite1 %'),
		'carbides_percent':fields.float('Carbides(%)'),
		'carbides_percent_max':fields.float('Carbides1 %'),
		'flack_size':fields.float('Flack Size'),
		'flack_type':fields.float('Flack Type'),
		'test_cer':fields.selection([('requires','Required'),('notrequired','Not Required')],'Test Certificate'),	


		## Child Tables Declaration

	}
	
	_defaults = {
	
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.master', context=c),
		'active': True,
		'state': 'draft',
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'modify': 'no',
		'entry_mode': 'manual',
		
	}
	
	_sql_constraints = [
	
		('name', 'unique(name)', 'Name must be unique per Company !!'),
		('code', 'unique(code)', 'Code must be unique per Company !!'),
	]	
	
	## Basic Needs	


	def entry_cancel(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'approved':
						
			if rec.cancel_remark:
				self.write(cr, uid, ids, {'state': 'cancel','cancel_user_id': uid, 'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
			else:
				raise osv.except_osv(_('Cancel remark is must !!'),
					_('Enter the remarks in Cancel remarks field !!'))
		else:
			pass
			
		return True
		
		
	def entry_confirm(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'draft':
			self.write(cr, uid, ids, {'state': 'confirm','confirm_user_id': uid, 'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		
		else:
			pass
			
		return True		
		


	def entry_draft(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'cancel':			
			self.write(cr, uid, ids, {'state': 'draft','update_user_id': uid, 'update_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
			
		return True
		
	def entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'confirm':
			self.write(cr, uid, ids, {'state': 'approved','ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})			
		else:
			pass
			
		return True		
		
		
	def entry_reject(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'confirmed':
			
			if rec.remark:
				self.write(cr, uid, ids, {'state': 'reject','ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})
			else:
				raise osv.except_osv(_('Rejection remark is must !!'),
					_('Enter the remarks in rejection remark field !!'))
					
		else:
			pass
			
		return True		

	
	def unlink(self,cr,uid,ids,context=None):
		unlink_ids = []		
		for rec in self.browse(cr,uid,ids):	
			if rec.state not in ('draft','cancel'):				
				raise osv.except_osv(_('Warning!'),
						_('You can not delete this entry !!'))
			else:
				unlink_ids.append(rec.id)
		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		
		
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_metal_grade_master, self).write(cr, uid, ids, vals, context)	
		
		
	## Module Requirement

kg_metal_grade_master()
