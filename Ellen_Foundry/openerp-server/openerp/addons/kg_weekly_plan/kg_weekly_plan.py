from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import math
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime
dt_time = time.strftime('%m/%d/%Y %H:%M:%S')

class kg_weekly_plan(osv.osv):

	_name = "kg.weekly.plan"
	_description = "Weekly Plan"
	_order = "entry_date desc"
	
	_columns = {
	
		## Version 0.1
		
		## Basic Info	
		
		'name': fields.char('WP No' ,select=True,readonly=True),
		'entry_date':fields.date('WP Date',required=True),
		'remark': fields.text('Remarks'),	
		'note': fields.text('Notes'),	
		'state': fields.selection([('draft','Draft'),('confirmed','WFA'),('approved','Pending'),('in_progress','In Progress'),('completed','Completed'),('cancel','Cancelled')],'Status', readonly=True),
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
				
		'from_date':fields.date('From Date',required=True),
		'to_date':fields.date('To Date',required=True),
		'act1':fields.boolean('Act 1'),
		'act2':fields.boolean('Act 2'),
		'act3':fields.boolean('Act 3'),
		'act4':fields.boolean('Act 4'),
		'act5':fields.boolean('Act 5'),
		'act6':fields.boolean('Act 6'),
		'flag':fields.boolean('Flag'),
		'count':fields.float('Count'),
		'count1':fields.float('Count1'),
		
		## Child Tables Declaration
				
		'line_ids':fields.one2many('ch.weekly.plan.line', 'header_id', 'Line Details'),

	}
	

	_defaults = {
			
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg_weekly_plan', context=c),			
		'entry_date' : lambda * a: time.strftime('%Y-%m-%d'),
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'state': 'draft',		
		'active': True,
		'entry_mode': 'manual',
		'act1': False,
		'act2': False,
		'act3': False,
		'act4': False,
		'act5': False,
		'act6': False,	
		'flag': False,	
		'count': 0.00,	
		'count1': 0.00,	
	}
		
		
	def load_sch(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		wpl_obj = self.pool.get('ch.weekly.plan.line')
		pattern_obj = self.pool.get('kg.pattern.master')
		d1 =datetime.strptime(rec.from_date, "%Y-%m-%d")
		d2 =datetime.strptime(rec.to_date, "%Y-%m-%d")
		if ((d2 - d1).days) <0:
			raise osv.except_osv(
							_('Warning'),
							_('Please select the To date Correctly !!'))
		if ((d2 - d1).days) >=6:
			raise osv.except_osv(
							_('Warning'),
							_('Please select the Date with Maximum 6 Days Difference !!'))
		cr.execute("""select from_date,to_date,* from kg_weekly_plan where from_date <='%s' and to_date >='%s' and id != %s"""%(rec.from_date,rec.from_date,rec.id))
		week_rec_from = cr.dictfetchall();
		cr.execute("""select from_date,to_date,* from kg_weekly_plan where from_date <='%s' and to_date >='%s' and id != %s"""%(rec.to_date,rec.to_date,rec.id))
		week_rec_to = cr.dictfetchall();
		if week_rec_from or week_rec_to:
			raise osv.except_osv(
				_('Warning'),
				_('Weekly Plan Already Created For this Days !!'))
		cr.execute("""delete from ch_weekly_plan_line where header_id= %s"""%(ids[0]))
		cr.execute("""select id,product_id,pending_qty,uom_id,grade_id,header_id,so_line_id from ch_schedule_line as schl 
								where pending_qty >0 and 
								(select state from kg_schedule where id=schl.header_id) ='approved'""")
		sch_date = cr.dictfetchall();
		for i in sch_date:
			cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(i['product_id']))
			pattern_data =cr.dictfetchall();		
			if pattern_data:
				pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])				
				no_of_box =i['pending_qty'] / pattern_data[0]['no_of_cavity']
				no_of_box =math.ceil(no_of_box)
				pattern= pattern_rec.id
			else:
				no_of_box =0
				pattern =''
			wpl_obj.create(cr, uid, {
								'header_id':rec.id,
								'tot_box':no_of_box,
								'so_line_id':i['so_line_id'],
								'sch_line_id':i['id'],
								'sch_id':i['header_id'],
								'product_id':i['product_id'],
								'uom_id':i['uom_id'],
								'weekly_qty':i['pending_qty'],
								'pending_qty':i['pending_qty'],
								'grade_id':i['grade_id'],
								'pattern_ids':pattern,
							})
		return
		
		
	def daily_plan_create(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		wpl_obj = self.pool.get('ch.weekly.plan.line')		
		if rec.state =='approved' or rec.state =='in_progress':
			dp_obj = self.pool.get('kg.daily.plan')
			dpl_obj = self.pool.get('ch.daily.plan.line')
			pattern_obj = self.pool.get('kg.pattern.master')
			product_obj = self.pool.get('product.product')
			cr.execute("""select current_date """)	
			entry_date = cr.fetchone();
			cr.execute("""select * from kg_daily_plan where entry_mode ='auto' and daily_entry_date='%s' """%(entry_date[0]))	
			daily_rec = cr.dictfetchall()
			if daily_rec:
				raise osv.except_osv(
					_('Warning'),
					_('Daily Plan has been already created for this Day !!'))
			cr.execute("""select * from kg_daily_plan where entry_mode ='auto' and state in ('draft','confirmed')""")	
			daily_rec_1 = cr.dictfetchall()
			if daily_rec_1:
				raise osv.except_osv(
					_('Warning'),
					_('Please Approved the already created Daily Plan !!'))
			dp_id = dp_obj.create(cr, uid, {'daily_entry_date':entry_date[0],'entry_date':entry_date[0],'entry_mode':'auto','state':'draft',})	
			val1 =[]
			val2 =[]
			val3 =[]
			val4 =[]
			val5 =[]
			val6 =[]
			for i in rec.line_ids:
				if i.day1 >0:
					val1.append(i.id)
				if i.day2 >0:
					val2.append(i.id)
				if i.day3 >0:
					val3.append(i.id)
				if i.day4 >0:
					val4.append(i.id)
				if i.day5 >0:
					val5.append(i.id)
				if i.day6 >0:
					val6.append(i.id)
			if val1 and rec.act1 ==False:
				cr.execute("""select  * from ch_weekly_plan_line where id in %s"""%(str('(%s)'%','.join(map(repr,tuple(val1))))))
				wpl_line_data =cr.dictfetchall();
				if wpl_line_data:
					for j in wpl_line_data:
						cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(j['product_id']))
						pattern_data =cr.dictfetchall();
						product_rec = product_obj.browse(cr,uid,j['product_id'])	
						weight = product_rec.piece_wgt * i.day1
						if pattern_data:
							pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])		
							no_of_box =float(j['day1']) / float(pattern_data[0]['no_of_cavity'])
							pattern = pattern_rec.pouring_wgt
							cavity = 	pattern_data[0]['no_of_cavity']							
						else:
							pattern = ''
							cavity = 	0
							no_of_box =0.0
						dpl_obj.create(cr, uid, {
								'header_id':dp_id,
								'product_id':j['product_id'],
								'uom_id':j['uom_id'],
								'grade_id':j['grade_id'],
								'so_line_id':j['so_line_id'],
								'sch_line_id':j['sch_line_id'],
								'tot_box':math.ceil(no_of_box),
								'order_qty':j['day1'] + j['remain_dpl_qty'],
								'daily_qty':j['day1'] + j['remain_dpl_qty'],
								'sch_qty':j['day1'],
								'entry_mode':'from_wp',
								'week_id':rec.id,
								'week_line_id':j['id'],
								'box_weight':pattern,
								'tot_weight':weight,
								'cavity':cavity,
							})			
					cr.execute("""update kg_weekly_plan set state='in_progress',act1 ='t',count = %s where id =%s"""%(rec.count +1,rec.id))	
			elif val2 and rec.act2 ==False:
				cr.execute("""select  * from ch_weekly_plan_line where id in %s"""%(str('(%s)'%','.join(map(repr,tuple(val2))))))
				wpl_line_data =cr.dictfetchall();
				if wpl_line_data:
					for j in wpl_line_data:
						cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(j['product_id']))
						pattern_data =cr.dictfetchall();
						product_rec = product_obj.browse(cr,uid,j['product_id'])	
						weight = product_rec.piece_wgt * i.day2
						if pattern_data:
							pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])		
							no_of_box =float(j['day2']) / float(pattern_data[0]['no_of_cavity'])
							pattern = pattern_rec.pouring_wgt
							cavity = 	pattern_data[0]['no_of_cavity']							
						else:
							pattern = ''
							cavity = 	0
							no_of_box =0.0
						dpl_obj.create(cr, uid, {
								'header_id':dp_id,
								'product_id':j['product_id'],
								'uom_id':j['uom_id'],
								'grade_id':j['grade_id'],
								'so_line_id':j['so_line_id'],
								'sch_line_id':j['sch_line_id'],
								'tot_box':math.ceil(no_of_box),
								'order_qty':j['day2'] + j['remain_dpl_qty'],
								'daily_qty':j['day2'] + j['remain_dpl_qty'],
								'sch_qty':j['day2'],
								'entry_mode':'from_wp',
								'week_id':rec.id,
								'week_line_id':j['id'],
								'box_weight':pattern,
								'tot_weight':weight,
								'cavity':cavity,
							})		
					cr.execute("""update kg_weekly_plan set state='in_progress',act2 ='t',count = %s where id =%s"""%(rec.count +1,rec.id))	
			elif val3 and rec.act3 ==False:
				cr.execute("""select  * from ch_weekly_plan_line where id in %s"""%(str('(%s)'%','.join(map(repr,tuple(val3))))))
				wpl_line_data =cr.dictfetchall();
				if wpl_line_data:
					for j in wpl_line_data:
						cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(j['product_id']))
						pattern_data =cr.dictfetchall();
						product_rec = product_obj.browse(cr,uid,j['product_id'])		
						weight = product_rec.piece_wgt * i.day3
						if pattern_data:
							pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])		
							no_of_box =float(j['day3']) / float(pattern_data[0]['no_of_cavity'])
							pattern = pattern_rec.pouring_wgt
							cavity = 	pattern_data[0]['no_of_cavity']							
						else:
							pattern = ''
							cavity = 	0
							no_of_box =0.0
						dpl_obj.create(cr, uid, {
								'header_id':dp_id,
								'product_id':j['product_id'],
								'uom_id':j['uom_id'],
								'grade_id':j['grade_id'],
								'so_line_id':j['so_line_id'],
								'sch_line_id':j['sch_line_id'],
								'tot_box':math.ceil(no_of_box),
								'order_qty':j['day3'] + j['remain_dpl_qty'],
								'daily_qty':j['day3'] + j['remain_dpl_qty'],
								'sch_qty':j['day3'],
								'entry_mode':'from_wp',
								'week_id':rec.id,
								'week_line_id':j['id'],
								'box_weight':pattern,
								'tot_weight':weight,
								'cavity':cavity,
							})					
					cr.execute("""update kg_weekly_plan set state='in_progress',act3 ='t',count = %s where id =%s"""%(rec.count +1,rec.id))	
			elif val4 and rec.act4 ==False:
				cr.execute("""select  * from ch_weekly_plan_line where id in %s"""%(str('(%s)'%','.join(map(repr,tuple(val4))))))
				wpl_line_data =cr.dictfetchall();
				if wpl_line_data:
					for j in wpl_line_data:
						cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(j['product_id']))
						pattern_data =cr.dictfetchall();
						product_rec = product_obj.browse(cr,uid,j['product_id'])		
						weight = product_rec.piece_wgt * i.day4
						if pattern_data:
							pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])		
							no_of_box =float(j['day4']) / float(pattern_data[0]['no_of_cavity'])
							pattern = pattern_rec.pouring_wgt
							cavity = 	pattern_data[0]['no_of_cavity']							
						else:
							pattern = ''
							cavity = 	0
							no_of_box =0.0
						dpl_obj.create(cr, uid, {
								'header_id':dp_id,
								'product_id':j['product_id'],
								'uom_id':j['uom_id'],
								'grade_id':j['grade_id'],
								'so_line_id':j['so_line_id'],
								'sch_line_id':j['sch_line_id'],
								'tot_box':math.ceil(no_of_box),
								'order_qty':j['day4'] + j['remain_dpl_qty'],
								'daily_qty':j['day4'] + j['remain_dpl_qty'],
								'sch_qty':j['day4'],
								'entry_mode':'from_wp',
								'week_id':rec.id,
								'week_line_id':j['id'],
								'box_weight':pattern,
								'tot_weight':weight,
								'cavity':cavity,
							})	
					cr.execute("""update kg_weekly_plan set state='in_progress',act4 ='t',count = %s where id =%s"""%(rec.count +1,rec.id))		
			elif val5 and rec.act5 ==False:
				cr.execute("""select  * from ch_weekly_plan_line where id in %s"""%(str('(%s)'%','.join(map(repr,tuple(val5))))))
				wpl_line_data =cr.dictfetchall();
				if wpl_line_data:
					for j in wpl_line_data:
						cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(j['product_id']))
						pattern_data =cr.dictfetchall();
						product_rec = product_obj.browse(cr,uid,j['product_id'])		
						weight = product_rec.piece_wgt * i.day5
						if pattern_data:
							pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])		
							no_of_box =float(j['day5']) / float(pattern_data[0]['no_of_cavity'])
							pattern = pattern_rec.pouring_wgt
							cavity = 	pattern_data[0]['no_of_cavity']							
						else:
							pattern = ''
							cavity = 	0
							no_of_box =0.0
						dpl_obj.create(cr, uid, {
								'header_id':dp_id,
								'product_id':j['product_id'],
								'uom_id':j['uom_id'],
								'grade_id':j['grade_id'],
								'so_line_id':j['so_line_id'],
								'sch_line_id':j['sch_line_id'],
								'tot_box':math.ceil(no_of_box),
								'order_qty':j['day5'] + j['remain_dpl_qty'],
								'daily_qty':j['day5'] + j['remain_dpl_qty'],
								'sch_qty':j['day5'],
								'entry_mode':'from_wp',
								'week_id':rec.id,
								'week_line_id':j['id'],
								'box_weight':pattern,
								'tot_weight':weight,
								'cavity':cavity,
							})			
					cr.execute("""update kg_weekly_plan set state='in_progress',act5 ='t',count = %s where id =%s"""%(rec.count +1,rec.id))		
			elif val6  and rec.act6 == False:
				cr.execute("""select  * from ch_weekly_plan_line where id in %s"""%(str('(%s)'%','.join(map(repr,tuple(val6))))))
				wpl_line_data =cr.dictfetchall();
				if wpl_line_data:
					for j in wpl_line_data:
						cr.execute("""select  no_of_cavity,header_id from kg_pattern_master_line where product_id= %s"""%(j['product_id']))
						pattern_data =cr.dictfetchall();
						product_rec = product_obj.browse(cr,uid,j['product_id'])	
						weight = product_rec.piece_wgt * i.day6	
						if pattern_data:
							pattern_rec = pattern_obj.browse(cr,uid,pattern_data[0]['header_id'])		
							no_of_box =float(j['day6']) / float(pattern_data[0]['no_of_cavity'])
							pattern = pattern_rec.pouring_wgt
							cavity = 	pattern_data[0]['no_of_cavity']							
						else:
							pattern = ''
							cavity = 	0
							no_of_box =0.0
						dpl_obj.create(cr, uid, {
								'header_id':dp_id,
								'product_id':j['product_id'],
								'uom_id':j['uom_id'],
								'grade_id':j['grade_id'],
								'so_line_id':j['so_line_id'],
								'sch_line_id':j['sch_line_id'],
								'tot_box':math.ceil(no_of_box),
								'order_qty':j['day6'] + j['remain_dpl_qty'],
								'daily_qty':j['day6'] + j['remain_dpl_qty'],
								'sch_qty':j['day6'],
								'entry_mode':'from_wp',
								'week_id':rec.id,
								'week_line_id':j['id'],
								'box_weight':pattern,
								'tot_weight':weight,
								'cavity':cavity,
							})		
					cr.execute("""update kg_weekly_plan set state='in_progress',act6 ='t',count = %s where id =%s"""%(rec.count +1,rec.id))		
		if (rec.count+1) == rec.count1:
			cr.execute("""update kg_weekly_plan set state ='completed' where id =%s"""%(rec.id))	
		return
		
		
		
	def entry_confirm(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])

		### Sequence Number Generation  ###

		if rec.state == 'draft':		
			if rec.name == '' or rec.name == False:
				seq_obj_id = self.pool.get('ir.sequence').search(cr,uid,[('code','=','kg.weekly.plan')])
				seq_rec = self.pool.get('ir.sequence').browse(cr,uid,seq_obj_id[0])
				cr.execute("""select generatesequenceno(%s,'%s','%s') """%(seq_obj_id[0],seq_rec.code,rec.entry_date))
				entry_name = cr.fetchone();
				entry_name = entry_name[0]	
			else:
				entry_name = rec.name	
			d1 =datetime.strptime(rec.from_date, "%Y-%m-%d")
			d2 =datetime.strptime(rec.to_date, "%Y-%m-%d")
			if ((d2 - d1).days) <0:
				raise osv.except_osv(
								_('Warning'),
								_('Please select the To date Correctly !!'))
			if ((d2 - d1).days) >=6:
				raise osv.except_osv(
								_('Warning'),
								_('Please select the Date with Maximum 6 Days Difference !!'))		
			for k in rec.line_ids:				
				lis =[]
				lis.append(k.day1)
				lis.append(k.day2)
				lis.append(k.day3)
				lis.append(k.day4)
				lis.append(k.day5)
				lis.append(k.day6)
				if ((d2-d1).days) !=(sum(l > 0.00 for l in lis))-1:
					raise osv.except_osv(
					_('Warning'),
					_('Please enter the correct values in Line item days !!'))			
			cr.execute("""select from_date,to_date,* from kg_weekly_plan where from_date <='%s' and to_date >='%s' and id != %s"""%(rec.from_date,rec.from_date,rec.id))
			week_rec_from = cr.dictfetchall();
			cr.execute("""select from_date,to_date,* from kg_weekly_plan where from_date <='%s' and to_date >='%s' and id != %s"""%(rec.to_date,rec.to_date,rec.id))
			week_rec_to = cr.dictfetchall();
			if week_rec_from or week_rec_to:
				raise osv.except_osv(
					_('Warning'),
					_('Weekly Plan Already Created For this Days !!'))			
			if not rec.line_ids:
				raise osv.except_osv(
							_('Warning'),
							_('You cannot allow to save with 0 order line'))
			for i in rec.line_ids:
				if i.total <=0:
					raise osv.except_osv(
							_('Warning'),
							_('System not allow to save with 0 total quantity'))					
				tot_qty =i.day1+i.day2+i.day3+i.day4+i.day5+i.day6
				if tot_qty >i.pending_qty:
					raise osv.except_osv(
							_('Warning'),
							_('6 Days Total Quantity Must be equal or smaller than Pending qty'))
			self.write(cr, uid, ids, {'name':entry_name,'state': 'confirmed','confirm_user_id': uid, 'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})
		else:
			pass
		return True						


	def entry_approve(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		wpl_obj = self.pool.get('ch.weekly.plan.line')
		if rec.state == 'confirmed':	
			val1 =[]
			val2 =[]
			val3 =[]
			val4 =[]
			val5 =[]
			val6 =[]
			count =0
			for i in rec.line_ids:
				if i.day1 >0:
					val1.append(i.id)
				if i.day2 >0:
					val2.append(i.id)
				if i.day3 >0:
					val3.append(i.id)
				if i.day4 >0:
					val4.append(i.id)
				if i.day5 >0:
					val5.append(i.id)
				if i.day6 >0:
					val6.append(i.id)
			if val1:
				count +=1
			if val2:
				count +=1
			if val3:
				count +=1
			if val4:
				count +=1
			if val5:
				count +=1
			if val6:
				count +=1
			d1 =datetime.strptime(rec.from_date, "%Y-%m-%d")
			d2 =datetime.strptime(rec.to_date, "%Y-%m-%d")
			if ((d2 - d1).days) <0:
				raise osv.except_osv(
								_('Warning'),
								_('Please select the To date Correctly !!'))
			if ((d2 - d1).days) >=6:
				raise osv.except_osv(
								_('Warning'),
								_('Please select the Date with Maximum 6 Days Difference !!'))		
			cr.execute("""select from_date,to_date,* from kg_weekly_plan where from_date <='%s' and to_date >='%s' and id != %s"""%(rec.from_date,rec.from_date,rec.id))
			week_rec_from = cr.dictfetchall();
			cr.execute("""select from_date,to_date,* from kg_weekly_plan where from_date <='%s' and to_date >='%s' and id != %s"""%(rec.to_date,rec.to_date,rec.id))
			week_rec_to = cr.dictfetchall();
			if week_rec_from or week_rec_to:
				raise osv.except_osv(
					_('Warning'),
					_('Weekly Plan Already Created For this Days !!'))		
			if not rec.line_ids:
				raise osv.except_osv(
						_('Warning'),
						_('You cannot allow to save with 0 order line'))		
			for i in rec.line_ids:
				tot_qty =i.day1+i.day2+i.day3+i.day4+i.day5+i.day6
				if tot_qty >i.pending_qty:
					raise osv.except_osv(
							_('Warning'),
							_('6 Days Total Quantity Must be equal or smaller than Pending qty'))
				remain_qty = i.pending_qty - i.total
				cr.execute("""update ch_schedule_line set pending_qty=%s where id =%s """%(remain_qty,i.sch_line_id.id))
			self.write(cr, uid, ids, {'state': 'approved','count1': count,'ap_rej_user_id': uid, 'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')})
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
		return super(kg_weekly_plan, self).create(cr, uid, vals, context=context)
		
		
	def write(self, cr, uid, ids, vals, context=None):
		vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),'update_user_id':uid})
		return super(kg_weekly_plan, self).write(cr, uid, ids, vals, context)		
		
				
	_sql_constraints = [
	
		('name', 'unique(name)', 'No must be Unique !!'),
	]					
	

kg_weekly_plan()


class ch_weekly_plan_line(osv.osv):

	_name = "ch.weekly.plan.line"
	_description = "Weekly Plan Line"
	
	_columns = {
	
		## Basic Info
		
		'header_id':fields.many2one('kg.weekly.plan', 'Weekly Plan', required=1, ondelete='cascade'),
		'remark': fields.text('Remarks'),
		'active': fields.boolean('Active'),			
		
		## Module Requirement Fields		
		
		'product_id':fields.many2one('product.product','Product',required=True,domain=[('product_type','=','finished_items'),('state','=','approved')]),
		'uom_id':fields.many2one('product.uom','UOM',readonly=True),
		'so_line_id':fields.many2one('sale.order.line','Sale Order Line No',readonly =True),
		'sch_id':fields.many2one('kg.schedule','SCH',readonly=True),
		'sch_line_id':fields.many2one('ch.schedule.line','SCH Line',readonly=True),
		'weekly_qty':fields.float('SCH Qty'),
		'pending_qty':fields.float('Pending Qty'),
		'tot_box':fields.float('Total Boxes'),
		'total':fields.float('Total'),
		'day1':fields.float('Day 1'),
		'day2':fields.float('Day 2'),
		'day3':fields.float('Day 3'),
		'day4':fields.float('Day 4'),
		'day5':fields.float('Day 5'),
		'day6':fields.float('Day 6'),
		'remain_dpl_qty':fields.float('Remaining Qty'),
		'grade_id': fields.many2one('kg.metal.grade.master','Grade',domain="[('state','=','approved')]"),
		'pattern_ids': fields.many2one('kg.pattern.master','Pattern',required=True,domain="[('state','=','approved')]"),
		'daily_state': fields.selection([('d1','D1'),('d2','D2'),('d3','D3'),('d4','D4'),('d5','D5'),('d6','D6'),('done','Done')],'Entry Mode', readonly=True),				
	}
	
	
	def onchange_qty(self, cr, uid, ids, day1 ,day2 ,day3 ,day4 ,day5 ,day6 ,total,pending_qty ,context=None):
		tot =day1+ day2+ day3+ day4+ day5+ day6
		if tot > pending_qty:
			raise osv.except_osv(
				_('Warning'),
				_('Total Quantity Must be Less than the Pending Quantity !!! '))
		return {'value': {'total':tot,}}
		
			
	
	
	_defaults = {
		
		'active': True,
		'daily_state': 'd1',
		'remain_dpl_qty': 0.00,
		
	}	
	
	
ch_weekly_plan_line()
	
