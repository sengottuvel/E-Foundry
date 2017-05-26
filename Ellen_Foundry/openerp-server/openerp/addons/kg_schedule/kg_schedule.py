from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')

class kg_schedule(osv.osv):

	_name = "kg.schedule"
	_description = "Schedule"
	_order = "name desc"
	
	_columns = {
	
		## Version 0.1
		
		## Basic Info	
		
		'name': fields.char('Schedule No' ,select=True,readonly=True),
		'entry_date':fields.date('Schedule Date',required=True),
		'remark': fields.text('Remarks'),	
		'note': fields.text('Notes'),	
		'state': fields.selection([('draft','Draft'),('confirmed','WFA'),('approved','Approved'),('cancel','Cancelled')],'Status', readonly=True),
		'entry_mode': fields.selection([('auto','Auto'),('manual','Manual')],'Entry Mode', readonly=True),
		'flag_sms': fields.boolean('SMS Notification'),
		'flag_email': fields.boolean('Email Notification'),
		'flag_spl_approve': fields.boolean('Special Approval'),

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
				
		'customer_id':fields.many2one('res.partner','Customer',required=True,domain=[('customer','=',True),('sup_state','=','approved')]),
		'so_nos':fields.many2many('sale.order','multiple_saleorder','schedule_id','so_id','Sale Order No',domain="[('state','=','approved'),('type_of_delivery','=','partial'),('partner_id','=',customer_id),('order_line.pending_qty','>','0')]"),
		'customer_po': fields.char('Customer PO.No' ,size=64),
		'so_date':fields.date('SO Date'),
		'customer_address': fields.char('Customer Address' ,readonly=True),
		'customer_code': fields.char('Customer Code' ,readonly=True),
		'customer_po_sch': fields.char('Customer SCH PO No' ,size=64),
		'customer_po_sch_date':fields.date('Customer SCH PO Date'),
		
		
		## Child Tables Declaration
				
		'line_ids':fields.one2many('ch.schedule.line', 'header_id', 'Line Details'),

	}
	

	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg_schedule', context=c),			
		'entry_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'state': 'draft',		
		'active': True,
		'entry_mode': 'manual',
		'flag_sms': False,		
		'flag_email': False,		
		'flag_spl_approve': False,				
	
	}
	
	

	def onchange_customer_id(self, cr, uid, ids, part, customer_address,customer_code,context=None):
		part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
		val = {
			'customer_address': part.street,
			'customer_code': part.code,
		}
		return {'value': val}
		
		
	def load_so(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		val =[]
		sch_line_obj = self.pool.get('ch.schedule.line')
		sql = """delete from ch_schedule_line where header_id= %s"""%(ids[0])		
		cr.execute(sql)	
		for i in rec.so_nos:
			val.append(str(i.customer_po))
			value = ",".join(val)
			for j in i.order_line:
				if j.pending_qty !=0:
					sch_line_id = sch_line_obj.create(cr, uid, {
								'header_id':rec.id,
								'grade_id':j.grade_id.id,
								'so_line_id':j.id,
								'customer_id':rec.customer_id.id,
								'product_id':j.product_id.id,
								'production_id':j.product_id.production_unit_id.id,
								'schedule_qty':j.pending_qty,
								'pending_qty':j.pending_qty,
								'order_qty':j.pending_qty,
								'uom_id': j.product_uom.id,
								'schedule_date': j.delivery_date,
								'line_state': 'pending',
								'entry_mode': 'from_so',
							})
					cr.execute("""insert into multiple_saleorder_line values(%s,%s)"""%(sch_line_id,j.order_id.id,))
							
				self.write(cr, uid, ids, {'customer_po':value})	
		return True
		
	
		
		
	def entry_confirm(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])

		### Sequence Number Generation  ###

		if rec.state == 'draft':		
			if rec.name == '' or rec.name == False:
				seq_obj_id = self.pool.get('ir.sequence').search(cr,uid,[('code','=','kg.schedule')])
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
				if i.schedule_qty <=0:
					raise osv.except_osv(
						_('Warning'),
						_('You cannot allow to save with 0 schedule qty'))
				if i.entry_mode =='from_so':
					if i.schedule_qty >i.order_qty:
						raise osv.except_osv(
							_('Warning'),
							_('Schedule Qty Must be smaller than the Order Qty'))
			self.write(cr, uid, ids, {'name':entry_name,'state': 'confirmed','confirm_user_id': uid, 'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
			
		return True						


	def entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'confirmed':	
			if not rec.line_ids:
				raise osv.except_osv(
						_('Warning'),
						_('You cannot allow to save with 0 order line'))		
			for i in rec.line_ids:
				if i.entry_mode =='from_so':				
					if i.schedule_qty >i.order_qty:
						raise osv.except_osv(
							_('Warning'),
							_('Schedule Qty Must be smaller than the Order Qty'))
					cr.execute("""update sale_order_line set pending_qty=%s where id =%s"""%(i.order_qty - i.schedule_qty,i.so_line_id.id))
			self.write(cr, uid, ids, {'state': 'approved','ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
			
		return True			
		
		
	def entry_cancel(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'approved':
			self.write(cr, uid, ids, {'state': 'cancel','cancel_user_id': uid, 'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
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
		return super(kg_schedule, self).create(cr, uid, vals, context=context)
		
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_schedule, self).write(cr, uid, ids, vals, context)		
				
				
	_sql_constraints = [
	
		('name', 'unique(name)', 'No must be Unique !!'),
	]					

kg_schedule()


class ch_schedule_line(osv.osv):

	_name = "ch.schedule.line"
	_description = "Schedule Line"
	
	_columns = {
	
		## Basic Info
		
		'header_id':fields.many2one('kg.schedule', 'Schedule No', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		'active': fields.boolean('Active'),			
		
		## Module Requirement Fields		
		
		'grade_id': fields.many2one('kg.metal.grade.master','Grade',required=True,domain="[('state','=','approved')]"),
		'customer_id':fields.many2one('res.partner','Customer',required=True,domain=[('customer','=',True),('sup_state','=','approved')]),
		'so_nos':fields.many2many('sale.order','multiple_saleorder_line','schedule_id','so_id','Sale Order No',domain="[('state','=','approved'),('type_of_delivery','=','partial'),('partner_id','=',customer_id),('order_line.pending_qty','>','0')]"),
		'entry_mode': fields.selection([('from_so','From SO'),('direct','Direct')],'Entry Mode', readonly=True),
		'so_line_id':fields.many2one('sale.order.line','Sale Order Line No',readonly =True),
		'product_id':fields.many2one('product.product','Product',required=True,domain=[('product_type','=','finished_items'),('state','=','approved')]),
		'uom_id':fields.many2one('product.uom','UOM',readonly=True),
		'order_qty':fields.float('Order Qty',readonly=True),
		'pending_qty':fields.float('Weekly/Daily Pending Qty',required=True),
		'schedule_qty':fields.float('Schedule Qty',required=True),
		'schedule_date':fields.date('Delivery Date',required=True),
		'production_id':fields.many2one('kg.production.unit','Production Unit Name',readonly=True,domain="[('state','=','approved')]"),
		'line_state': fields.selection([('pending','Pending'),('painting','Painting'),('qc_process','QC Process'),
				('done','Done')],'Line Status', readonly=True),
				
	}
	

	def onchange_product_id(self, cr, uid, ids, partn, uom_id,context=None):
		part = self.pool.get('product.template').browse(cr, uid, partn, context=context)
		product = self.pool.get('product.product').browse(cr, uid, partn, context=context)
		val = {
			'uom_id': part.uom_id.id,
			'production_id': product.production_unit_id.id,
		}
		return {'value': val}
		
	def onchange_schedule_qty(self, cr, uid, ids, schedule_qty, pending_qty,context=None):
		return {'value': {'pending_qty':schedule_qty}}
		
	
	
	_defaults = {
		
		'active': True,
		'line_state': 'pending',
		'entry_mode': 'direct',
		
	}	
	
	
ch_schedule_line()
	
