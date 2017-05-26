from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from datetime import datetime
import re
import math
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kg_employee(osv.osv):

	_name = "hr.employee"
	_inherit = "hr.employee"
	_description = "Employee"
	
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
					as sam  """ %('hr_employee'))
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
		
		'code':fields.char('Code',size=4),
		'state': fields.selection([('draft','Draft'),('confirm','WFA'),('approved','Approved'),
				('reject','Rejected'),('cancel','Cancelled')],'Status', readonly=True),
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


		## Child Tables Declaration

	}
	
	
	
	_defaults = {
	
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context=c),
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


#email validation
	def  _validate_email(self, cr, uid, ids, context=None):
		rec = self.browse(cr,uid,ids[0])	
		if rec.work_email==False:
			return True
		else:
			if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", rec.work_email) != None:
				return True
			else:
				raise osv.except_osv('Invalid Email', 'Please enter a valid email address in the Email Field')		
				
				
				
#validate mobile number

	def _validate_phone(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		if rec.mobile_phone:
			if len(str(rec.mobile_phone)) in (10,11,12) and rec.mobile_phone.isdigit() == True:
				return True
			else:
				return False
		return True		
		
		
#check Phone number
		
	def _check_phone(self, cr, uid, ids, context=None):		
		rec = self.browse(cr, uid, ids[0])
		if rec.work_phone:
			if len(str(rec.work_phone)) in (8,9,10,11,12,13,14,15) and rec.work_phone.isdigit() == True:
				return True
			else:
				return False
		return True		
			
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
		return super(kg_employee, self).write(cr, uid, ids, vals, context)	
		
	## Module Requirement
	
	
	_constraints = [
		(_validate_email, 'Enter a valid Email in the Email Field!!', ['work_email']),
		(_validate_phone, 'Enter a correct Mobile Number in Mobile Number Field!!', ['mobile_phone']),
		(_check_phone, 'Enter a correct Phone Number in Phone Number field!!', ['work_phone']),
       	]	
		
kg_employee()
