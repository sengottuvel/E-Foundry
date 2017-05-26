from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import math
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')

class kg_daily_plan(osv.osv):

	_name = "kg.daily.plan"
	_description = "Daily Plan"
	_order = "entry_date desc"
	
	_columns = {
	
		## Version 0.1
		
		## Basic Info	
		
		'name': fields.char('DP No' ,select=True,readonly=True),
		'entry_date':fields.date('DP Date',required=True,readonly=True),
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
		'sch_ids':fields.many2many('kg.schedule','multiple_schedule','dp_id','sch_id','Schedule No',domain="[('state','=','approved'),('line_ids.pending_qty','>','0')]"),
		'daily_entry_date':fields.date('WP Date',required=True),
		
		## Child Tables Declaration
				
		'line_ids':fields.one2many('ch.daily.plan.line', 'header_id', 'Line Details'),

	}
	

	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg_daily_plan', context=c),			
		'entry_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'daily_entry_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'state': 'draft',		
		'active': True,
		'entry_mode': 'manual',
	
	}
		
		
	def load_sch(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		dpl_obj = self.pool.get('ch.daily.plan.line')
		pattern_obj = self.pool.get('kg.pattern.master')
		product_obj = self.pool.get('product.product')
		cr.execute("""delete from ch_daily_plan_line where  entry_mode ='direct' and header_id= %s"""%(ids[0]))
		for j in rec.sch_ids:
			cr.execute("""select id,product_id,pending_qty,uom_id,production_id,grade_id,header_id,so_line_id from ch_schedule_line as schl 
									where pending_qty >0 and 
									(select state from kg_schedule where id=schl.header_id) ='approved' and header_id = %s"""%(j.id))
			sch_data = cr.dictfetchall();
			for i in sch_data:
				cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(i['product_id']))
				pattern_data =cr.dictfetchall();		
				product_rec = product_obj.browse(cr,uid,i['product_id'])			
				if pattern_data:
					pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])	
					no_of_box =i['pending_qty'] / pattern_data[0]['no_of_cavity']
					no_of_box =math.ceil(no_of_box)
					pattern =pattern_rec.pouring_wgt
					cavity = pattern_data[0]['no_of_cavity']
				else:
					pattern =''
					no_of_box =0
					cavity =0
				dpl_obj.create(cr, uid, {
									'header_id':rec.id,
									'product_id':i['product_id'],
									'uom_id':i['uom_id'],
									'production_id':i['production_id'],
									'grade_id':i['grade_id'],
									'so_line_id':i['so_line_id'],
									'sch_line_id':i['id'],
									'tot_box':no_of_box,
									'order_qty':i['pending_qty'],
									'daily_qty':i['pending_qty'],
									'sch_qty':i['pending_qty'],
									'entry_mode':'direct',
									'box_weight':pattern,
									'tot_weight':product_rec.piece_wgt * i['pending_qty'],
									'cavity':cavity,
								})
		return		
				
		
	def entry_confirm(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])

		### Sequence Number Generation  ###

		if rec.state == 'draft':		
			if rec.name == '' or rec.name == False:
				seq_obj_id = self.pool.get('ir.sequence').search(cr,uid,[('code','=','kg.daily.plan')])
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
				if not i.heat_no:
					raise osv.except_osv(
							_('Warning'),
							_('Please Enter Heat No in the Line Items'))
				if i.sch_qty < i.daily_qty:
					raise osv.except_osv(
							_('Warning'),
							_('Daily Quantity Must be smaller than the Schedule Qty'))
			self.write(cr, uid, ids, {'name':entry_name,'state': 'confirmed','confirm_user_id': uid, 'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
		return True						


	def entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		mol_obj = self.pool.get('kg.moulding')
		mol_li_obj = self.pool.get('ch.moulding.line')
		if rec.state == 'confirmed':	
			if not rec.line_ids:
				raise osv.except_osv(
							_('Warning'),
							_('You cannot allow to save with 0 order line'))
			for i in rec.line_ids:
				if not i.heat_no:
					raise osv.except_osv(
							_('Warning'),
							_('Please Enter Heat No in the Line Items'))
				if i.entry_mode =='auto':
					cr.execute("""update ch_weekly_plan_line set remain_dpl_qty =%s where id = %s"""%(i.order_qty - i.daily_qty,i.week_line_id.id))
				if i.sch_qty < i.daily_qty:
					raise osv.except_osv(
							_('Warning'),
							_('Daily Quantity Must be smaller than the Schedule Qty'))		
				if rec.entry_mode =='manual':
					cr.execute("""update ch_schedule_line set pending_qty =%s where id = %s"""%(i.sch_qty -i.daily_qty,i.sch_line_id.id))
			mol_id = mol_obj.create(cr, uid, {'daily_id':rec.id,'daily_plan_date':rec.entry_date,'entry_mode':'auto','state':'draft',})	
			for i in rec.line_ids:
				mol_li_obj.create(cr, uid, {
					'header_id':mol_id,
					'product_id':i.product_id.id,
					'uom_id':i.uom_id.id,
					'production_id':i.production_id.id,
					'grade_id':i.grade_id.id,
					'so_line_id':i.so_line_id.id,
					'sch_line_id':i.sch_line_id.id,
					'week_line_id':i.week_line_id.id,
					'daily_id':rec.id,
					'daily_line_id':i.id,
					'tot_box':i.tot_box,
					'heat_no':i.heat_no,
					'daily_qty':i.daily_qty,
					'mould_produce':i.daily_qty,
					'mould_reject':0.00,
					'entry_mode':'from_dp',
					})						
			self.write(cr, uid, ids, {'state': 'approved','ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
		return True			
		

		
	def unlink(self,cr,uid,ids,context=None):
		unlink_ids = []		
		for rec in self.browse(cr,uid,ids):	
			if rec.state != 'draft' or rec.entry_mode =='auto':			
				raise osv.except_osv(_('Warning!'),
						_('You can not delete this entry !!'))
			else:
				unlink_ids.append(rec.id)
		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)	
			
			
	def create(self, cr, uid, vals, context=None):
		return super(kg_daily_plan, self).create(cr, uid, vals, context=context)
		
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_daily_plan, self).write(cr, uid, ids, vals, context)		
		
				
	_sql_constraints = [
	
		('name', 'unique(name)', 'No must be Unique !!'),
	]					
	

kg_daily_plan()


class ch_daily_plan_line(osv.osv):

	_name = "ch.daily.plan.line"
	_description = "Daily Plan Line"
	
	_columns = {
	
		## Basic Info
		
		'header_id':fields.many2one('kg.daily.plan', 'Daily Plan', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		'active': fields.boolean('Active'),			
		
		## Module Requirement Fields		
		
		'product_id':fields.many2one('product.product','Product',required=True,domain=[('product_type','=','finished_items'),('state','=','approved'),('active','=',True)]),
		'uom_id':fields.many2one('product.uom','UOM'),
		'production_id':fields.many2one('kg.production.unit','Production Unit Name',domain="[('state','=','approved')]"),
		'grade_id': fields.many2one('kg.metal.grade.master','Grade',domain="[('state','=','approved')]"),
		'so_line_id':fields.many2one('sale.order.line','Sale Order Line No'),
		'sch_line_id':fields.many2one('ch.schedule.line','SCH Line'),
		'week_id':fields.many2one('kg.weekly.plan','Weekly Plan'),
		'week_line_id':fields.many2one('ch.weekly.plan.line','Weekly Plan Line'),
		'sch_qty':fields.float('Order Qty',required=True),
		'daily_qty':fields.float('Daily Qty',required=True),
		'order_qty':fields.float('Order Qty',required=True),
		'heat_no':fields.char('Heat No'),
		'tot_box':fields.float('No.of Boxes'),
		'box_weight':fields.float('Box Weight'),
		'tot_weight':fields.float('Total Weight'),
		'cavity':fields.float('Cavity'),
		'entry_mode': fields.selection([('direct','Direct'),('from_wp','From WP')],'Entry Mode'),
				
	}
	
	
	
	_defaults = {
		
		'active': True,
		'entry_mode': 'direct',
		
	}	
	
	
	_sql_constraints = [
	
		('heat_no', 'unique(heat_no)', 'Heat Number must be Unique !!'),
	]			
			
			
	def onchange_qty(self, cr, uid, ids, product_id , daily_qty , tot_box, tot_weight, cavity,context=None):
		product_obj = self.pool.get('product.product')
		product_rec = product_obj.browse(cr,uid,product_id)			
		if cavity !=0:
			no_of_box =float(daily_qty) / float(cavity)
		else:
			no_of_box =0
		return {'value': {'tot_box':math.ceil(no_of_box),'tot_weight':daily_qty * product_rec.piece_wgt}}
		
	
ch_daily_plan_line()
	
