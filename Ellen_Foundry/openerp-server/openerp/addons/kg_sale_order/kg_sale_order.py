from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')


class kg_sale_order(osv.osv):
	
	_name = "sale.order"
	_inherit = "sale.order"
	
	_columns = {
	
		## Version 0.1
		
		## Basic Info		
		
		'remark': fields.text('Remarks'),
		'entry_mode': fields.selection([('auto','Auto'),('manual','Manual')],'Entry Mode', readonly=True),
		'flag_sms': fields.boolean('SMS Notification'),
		'flag_email': fields.boolean('Email Notification'),
		'flag_spl_approve': fields.boolean('Special Approval'),

		## Entry Info
		
		'active': fields.boolean('Active'),
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'crt_date':fields.datetime('Created Date',readonly=True),
		'ap_rej_date': fields.datetime('Approved/Rejected Date', readonly=True),
		'ap_rej_user_id': fields.many2one('res.users', 'Approved/Rejected By', readonly=True),
		'cancel_user_id': fields.many2one('res.users', 'Cancelled By', readonly=True),
		'cancel_date': fields.datetime('Cancelled Date', readonly=True),
		'update_date': fields.datetime('Last Updated Date',readonly=True),
		'update_user_id': fields.many2one('res.users','Last Updated By',readonly=True),		
		'cancel_remark': fields.text('Cancel Remarks'),			
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),	

		## Module Requirement Info

		'customer_po': fields.char('Customer PO No',size=64,required=True),
		'customer_address': fields.char('Customer Address',size=64,readonly=True),
		'type_of_delivery':fields.selection([('one_time','One Time'),('partial','Partial')],'Type of Delivery',required=True),
		'customer_code': fields.char('Customer Code',size=64,readonly=True),
		'customer_po_date': fields.date('Customer PO Date', required=True),
		'mode_of_delivery':fields.selection([('by_sea','By Sea'),('by_air','By Air'),('by_road','By Road')],'Mode of Delivey ',required=True),
	
		
		
	}

	
	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'sale_order', context=c),			
		'crt_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'active': True,
		'entry_mode': 'manual',
		'flag_sms': False,		
		'flag_email': False,		
		'flag_spl_approve': False,				
	
	}	
	
	
	def _check_lineitems(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.order_line:
			return False
		return True
	
	_constraints = [		
			  
		(_check_lineitems, 'System not allow to save with empty Details !!',['']),
	   
	   ]	
	
	
	def so_entry_confirm(self,cr,uid,ids,context=None):		
	
		rec = self.browse(cr,uid,ids[0])

		### Sequence Number Generation  ###
		
		if rec.state == 'draft':		
			if rec.name == '' or rec.name == False:				
				seq_obj_id = self.pool.get('ir.sequence').search(cr,uid,[('code','=','sale.order')])
				seq_rec = self.pool.get('ir.sequence').browse(cr,uid,seq_obj_id[0])
				cr.execute("""select generatesequenceno(%s,'%s','%s') """%(seq_obj_id[0],seq_rec.code,rec.date_order))
				entry_name = cr.fetchone();
				entry_name = entry_name[0]		
			else:
				entry_name = rec.name					
						
			
			self.write(cr, uid, ids, {
					'state': 'confirm',
					'conf_user_id': uid,
					'confirm_date': dt_time,
					'name': entry_name,
					
					})
		else:
			pass
		return True	
		
		
		
	def so_entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		
		if rec.state == 'confirm':
			
			seq_obj_id_a = self.pool.get('ir.sequence').search(cr,uid,[('code','=','kg.schedule')])
			seq_rec_a = self.pool.get('ir.sequence').browse(cr,uid,seq_obj_id_a[0])
			cr.execute("""select generatesequenceno(%s,'%s','%s') """%(seq_obj_id_a[0],seq_rec_a.code,rec.date_order))
			entry_name_a = cr.fetchone();
			entry_name_a = entry_name_a[0]												
			sch_obj=self.pool.get('kg.schedule')
			sch_line_obj=self.pool.get('ch.schedule.line')		
			if rec.type_of_delivery =='one_time':
				schedule_ids = sch_obj.create(cr,uid,
						{
						'name':entry_name_a,
						'customer_id':rec.partner_id.id,
						'customer_po':rec.customer_po,
						'customer_address':rec.customer_address,
						'customer_code':rec.customer_code,
						'so_date':rec.date_order,
						'state':'approved',
						'entry_mode':'auto',
						})
				cr.execute("""insert into multiple_saleorder values(%s,%s)"""%(schedule_ids,rec.id))
				for i in rec.order_line:
					sch_line_id = sch_line_obj.create(cr,uid,
							{
							'header_id':schedule_ids,
							'grade_id':i.grade_id.id,
							'customer_id':rec.partner_id.id,
							'product_id':i.product_id.id,
							'production_id':i.product_id.production_unit_id.id,
							'schedule_qty':i.pending_qty,
							'pending_qty':i.pending_qty,
							'order_qty':i.pending_qty,
							'uom_id':i.product_uom.id,
							'schedule_date':i.delivery_date,
							'line_state':'pending',
							})
					cr.execute("""update sale_order_line set pending_qty=0 where order_id =%s"""%(rec.id))
					cr.execute("""insert into multiple_saleorder_line values(%s,%s)"""%(sch_line_id,rec.id,))
			
			self.write(cr, uid, ids, {'state': 'approved','ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		
		else:
			pass
					
		return True	
		
		
	def so_entry_cancel(self,cr,uid,ids,context=None):
		
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
		return super(kg_sale_order, self).create(cr, uid, vals, context=context)
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_sale_order, self).write(cr, uid, ids, vals, context)		
	
	
	
kg_sale_order()

class ch_sale_order_line(osv.osv):
	
	_name = "sale.order.line"
	_inherit = "sale.order.line"
	_columns = {
	
		## Basic Info
	
		'remark': fields.text('Remarks'),
		
		## Module Requirement Fields
	
		'order_date': fields.date('Order Date'),
		'delivery_date': fields.date('Delivery Date', required=True),
		'acc_tot_wgt': fields.float('Accepted Total Weight(Kgs)',required=True),
		'order_tot_wgt': fields.float('Order Total Weight(Kgs)',required=True),
		'order_qty': fields.float('Order Qty',required=True),
		'pending_qty': fields.float('Pending Qty',readonly=True),
		'acc_tot_wt': fields.float('Accepted Total Weight(Kgs)'),
		'cus_price': fields.float('Customer PO Price',required=True),
		'drawing_no': fields.many2one('kg.drawing.details','Drawing No',
					domain="[('draw_info','=','active'),'&',('header_id','=',product_id)]"),
		'drawing_rev_no': fields.char('Drawing Rev No', size=64,),
		'grade_id': fields.many2one('kg.metal.grade.master','Grade',required=True,domain="[('state','=','approved')]"),

		
		
	}
	
	
	
	def default_get(self, cr, uid, fields, context=None):
		
		return context	
	
	def _check_floatvalues(self, cr, uid, ids, context=None):
		rec = self.browse(cr,uid,ids[0])
		if rec.product_uom_qty > rec.order_qty:
			raise osv.except_osv(_('Warning!'),
						_('Accepted Qty Must be smaller than the Order Qty	 !!'))
		if rec.th_weight <=0.00 or rec.order_qty<=0 or rec.cus_price <=0:
			return False
		return True
		
	
	_constraints = [		
			  
		(_check_floatvalues, 'System not allow to save with 0 values in float fields !!',['']),
	   
	   ]		
	
	def onchange_drawing_id(self, cr, uid, ids, product_id,drawing_no,drawing_rev_no,context=None):
		drawing = self.pool.get('kg.drawing.details').browse(cr, uid, drawing_no, context=context)
		if drawing.id ==False:
			return True
		else:
			val = {'drawing_rev_no':drawing.drawing_rev_number}
		return {'value': val}	
		
		
	def onchange_piece_wgt(self, cr, uid, ids, th_weight,order_tot_wgt,acc_tot_wgt,pending_qty,order_qty,context=None):
		order_wgt = th_weight * order_qty
		acc_wgt = th_weight * pending_qty
		val = {'acc_tot_wgt':acc_wgt,'order_tot_wgt':order_wgt}	
		return {'value': val}	
		
	def onchange_order_qty(self, cr, uid, ids, th_weight,order_tot_wgt,acc_tot_wgt,context=None):
		vals =0.00
		val = {'th_weight':vals,'order_tot_wgt':vals,'acc_tot_wgt':vals}	
		return {'value': val}	

	

	
ch_sale_order_line()

