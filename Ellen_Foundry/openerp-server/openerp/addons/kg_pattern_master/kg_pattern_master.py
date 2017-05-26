from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from datetime import datetime
import re
import math
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kg_pattern_master(osv.osv):

	_name = "kg.pattern.master"
	_description = "Pattern Master"
	
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
					as sam  """ %('kg_pattern_master'))
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

		'box_size': fields.selection([('400*520','400*520'),('520*520','520*520'),('650*650','650*650')], 'Box Size',required=True),
		'no_of_melt':fields.float("No.of Melt/Day",required=True),
		'box_frame':fields.float('Box Frame(mm)',required=True),
		'moulding_sand': fields.selection([('green','Green Sand'),('a','A'),('b','B')], 'Moulding Sand',required=True),
		'sleeve_details': fields.selection([('exothermic','Exothermic'),('insulating','Insulating'),('nil','Nil')], 'Sleeve Details',required=True),
		'mould_hardness_min':fields.char('Mould Hardness (Min)',size=128,required=True),
		'mould_hardness_max':fields.char('Mould Hardness (Max)',size=128,required=True),
		'heat_code':fields.char('Heat Code Details',size=128,required=True),
		'pouring_wgt': fields.float('Box Weight(Kgs)',required=True),
		'metal_wgt': fields.float('Casting Weight(Kgs)',required=True),
		'grade_of_metal':fields.many2one('kg.metal.grade.master','Metal Grade',required=True,domain="[('state','=','approved')]"),
		'riser_details': fields.selection([('open','Open'),('close','Close'),('nil','Nil')], 'Riser Details',required=True),
		'riser_details':fields.char('Chill Details',size=128,required=True),
		'gc_min':fields.char('GC Strength (Min)',size=128,required=True),
		'gc_max':fields.char('GC Strength (Max)',size=128,required=True),
        'test_bar': fields.selection([('heel_block','Heel Block'),('test_bar','Test Bar')], 'Test Bar',required=True),
		'yields':fields.float('Yield(%)',required=True),

		## Child Tables Declaration

		'line_ids':fields.one2many('kg.pattern.master.line', 'header_id', 'Pattern Line'),
		
	}
	
	_defaults = {
	
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.master', context=c),
		'active': True,
		'state': 'draft',
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'modify': 'no',
		'entry_mode': 'manual',
		'moulding_sand': 'green',
		'sleeve_details': 'nil',
		
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
			if rec.pouring_wgt <=0 or rec.metal_wgt <=0 or rec.box_frame <=0 or rec.no_of_melt <=0 or rec.yields <= 0:
				raise osv.except_osv(_('Warning !!'),
					_('Float field values must be greater than 0 !!'))
			if rec.line_ids:
				for i in rec.line_ids:
					if i.no_of_cavity <=0:
						raise osv.except_osv(_('Warning !!'),
							_('Cavity must be greater than 0 !!'))

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
			if rec.pouring_wgt <=0 or rec.metal_wgt <=0 or rec.box_frame <=0 or rec.no_of_melt <=0 or rec.yields <= 0:
				raise osv.except_osv(_('Warning !!'),
					_('Float field values must be greater than 0 !!'))
			if rec.line_ids:
				for i in rec.line_ids:
					if i.no_of_cavity <=0:
						raise osv.except_osv(_('Warning !!'),
							_('Cavity must be greater than 0 !!'))
			
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
		return super(kg_pattern_master, self).write(cr, uid, ids, vals, context)	
		
		
	## Module Requirement

kg_pattern_master()


class kg_pattern_master_line(osv.osv):
	
	_name = "kg.pattern.master.line"
	_description = "Kg Pattern Master line"
	
	_columns = {
		
		## Basic Info
		
		'header_id': fields.many2one('kg.pattern.master', 'Header Id'),
		'remark': fields.text('Remarks'),
		'active': fields.boolean('Active'),			
		
		## Module Requirement Fields
		
		'product_id': fields.many2one('product.product','Product Name',domain="[('product_type','=','finished_items'),('state','=','approved')]"),
		'no_of_cavity':fields.float('No.of Cavity'),		
		
		## Child Tables Declaration
		
	}
		
	_defaults = {
	
		'active': True,
		
	}

	_sql_constraints = [
	
		('product_id', 'unique(product_id)', 'Pattern Already available for this product !!'),
	]			
		
kg_pattern_master_line()
