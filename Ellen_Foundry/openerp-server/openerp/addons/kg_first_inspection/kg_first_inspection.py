from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import math
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')

class kg_first_inspection(osv.osv):

	_name = "kg.first.inspection"
	_description = "First Stage Inspection"
	_order = "entry_date desc"
	
	_columns = {
	
		## Version 0.1
		
		## Basic Info	
		
		'name': fields.char('FSI No' ,select=True,readonly=True),
		'entry_date':fields.date('FSI Date',required=True),
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
		
		'melt_id':fields.many2one('kg.melting','Melting No',readonly=True),
		
		## Child Tables Declaration
				
		'line_ids':fields.one2many('ch.first.inspection.line', 'header_id', 'Line Details'),

	}
	

	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg_first_inspection', context=c),			
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
				seq_obj_id = self.pool.get('ir.sequence').search(cr,uid,[('code','=','kg.first.inspection')])
				seq_rec = self.pool.get('ir.sequence').browse(cr,uid,seq_obj_id[0])
				cr.execute("""select generatesequenceno(%s,'%s','%s') """%(seq_obj_id[0],seq_rec.code,rec.entry_date))
				entry_name = cr.fetchone();
				entry_name = entry_name[0]	
			else:
				entry_name = rec.name	
			if not rec.line_ids:
				raise osv.except_osv(
							_('Warning'),
							_('You cannot allow to save with 0 order line'))
			for i in rec.line_ids:
				if i.acc_qty + i.rej_qty > i.qty:
					raise osv.except_osv(
							_('Warning'),
							_('Please check the Product Quantity'))
			self.write(cr, uid, ids, {'name':entry_name,'state': 'confirmed','confirm_user_id': uid, 'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
		return True						


	def entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		fin_inspec_id = self.pool.get('kg.final.inspection')
		fin_inspec_line_id = self.pool.get('ch.final.inspection.line')				
		
		if rec.state == 'confirmed':	
			if not rec.line_ids:
				raise osv.except_osv(
							_('Warning'),
							_('You cannot allow to save with 0 order line'))		
			for i in rec.line_ids:
				if i.acc_qty + i.rej_qty > i.qty:
					raise osv.except_osv(
							_('Warning'),
							_('Please check the Product Quantity'))
			inspec_rec = fin_inspec_id.create(cr, uid, {'fis_ins_id':rec.id,'fis_insp_date':rec.entry_date,'entry_mode':'auto','state':'draft',})	
			for i in rec.line_ids:
				fin_inspec_line_id.create(cr, uid, {
					'header_id':inspec_rec,
					'product_id':i.product_id.id,
					'uom_id':i.uom_id.id,
					'production_id':i.production_id.id,
					'grade_id':i.grade_id.id,
					'so_line_id':i.so_line_id.id,
					'sch_line_id':i.sch_line_id.id,
					'week_line_id':i.week_line_id.id,
					'daily_line_id':i.daily_line_id.id,
					'mould_line_id':i.mould_line_id.id,
					'melt_line_id':i.melt_line_id.id,
					'melting_log_id':i.melting_log_id.id,
					'fis_id':rec.id,
					'fis_line_id':i.id,
					'heat_no':i.heat_no,
					'qty':i.acc_qty,
					'acc_qty':i.acc_qty,
					'entry_mode':'from_fisi',
					})									
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
		return super(kg_first_inspection, self).create(cr, uid, vals, context=context)
		
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_first_inspection, self).write(cr, uid, ids, vals, context)		
		
				
	_sql_constraints = [
	
		('name', 'unique(name)', 'No must be Unique !!'),
	]					
	

kg_first_inspection()


class ch_first_inspection_line(osv.osv):

	_name = "ch.first.inspection.line"
	_description = "First Inspection Line"
	
	_columns = {
	
		## Basic Info
		
		'header_id':fields.many2one('kg.first.inspection', 'First Stage Inspection', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		'active': fields.boolean('Active'),			
		
		## Module Requirement Fields		
		
		'product_id':fields.many2one('product.product','Product',required=True,domain=[('product_type','=','finished_items'),('state','=','approved'),('active','=',True)]),
		'uom_id':fields.many2one('product.uom','UOM',readonly=True),
		'production_id':fields.many2one('kg.production.unit','Production Unit Name',readonly=True,domain="[('state','=','approved')]"),
		'grade_id': fields.many2one('kg.metal.grade.master','Grade',domain="[('state','=','approved')]"),
		'so_line_id':fields.many2one('sale.order.line','Sale Order Line No',readonly =True),
		'sch_line_id':fields.many2one('ch.schedule.line','SCH Line',readonly=True),
		'week_line_id':fields.many2one('ch.weekly.plan.line','Weekly Plan Line',readonly=True),
		'daily_line_id':fields.many2one('ch.daily.plan.line','Daily Plan Line',readonly=True),
		'mould_line_id':fields.many2one('ch.moulding.line','Moulding Line',readonly=True),
		'melt_id':fields.many2one('kg.melting','Melting No',readonly=True),
		'melt_line_id':fields.many2one('ch.melting.line','Melting Line',readonly=True),
		'melting_log_id':fields.many2one('kg.melting.log','Furnance No',domain="[('state','=','approved')]"),
		'qty':fields.float('Quantity',readonly=True),
		'acc_qty':fields.float('Accepted Qty'),
		'rej_qty':fields.float('Rejected Qty'),
		'heat_no':fields.char('Heat No',required=True),
		'entry_mode': fields.selection([('direct','Direct'),('from_ml','From MP')],'Entry Mode', readonly=True),
				
	}
	
	
	
	_defaults = {
		
		'active': True,
		'entry_mode': 'direct',
		
	}	
	
	
ch_first_inspection_line()
	
