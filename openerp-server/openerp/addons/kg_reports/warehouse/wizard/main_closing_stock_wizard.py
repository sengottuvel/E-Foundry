import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
logger = logging.getLogger('server')
	
class main_closing_stock_wizard(osv.osv_memory):
		
	_name = 'main.closing.stock.wizard'
	_columns = {
		
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
		'date': fields.date("Date"),
		'location_dest_id': fields.many2one('stock.location', 'Stores', required=True, domain="[('location_type','=', 'main'),('state','=','approved')]"),
		'major_name':fields.many2one('product.category', 'Product Category',domain="[('state','=','approved')]"),
		'product':fields.many2many('product.product','main_close_stock_product','stock_product_id','close_stock_id','Product',domain="[('state','=','approved')]"),
		'product_type': fields.selection([('consu', 'Consumable Items'),('cap','Capital Goods'),('service','Service Items')], 'Product Type'),
		'company_id': fields.many2one('res.company', 'Company Name'),
		'pro_cat': fields.boolean('Stock by category'),
		
	}
	
	_defaults = {
		
		'filter': 'filter_date', 
		'date': time.strftime('%Y-%m-%d'),
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.depindent.detail.wizard', context=c),
		
	}
 
	def _build_contexts(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		result = {}
		result['date'] = 'date' in data['form'] and data['form']['date'] or False
		if data['form']['filter'] == 'filter_date':
			result['date'] = data['form']['date']
		return result
		
	def date_indian_format(self,date_pyformat):
		date_contents = date_pyformat.split("-")
		date_indian = date_contents[2]+"/"+date_contents[1]+"/"+date_contents[0]
		return date_indian
	  
	def check_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		data = {}
		data['ids'] = context.get('active_ids', [])
		data['model'] = context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(cr, uid, ids, [])[0]
		used_context = self._build_contexts(cr, uid, ids, data, context=context)
		data['form']['used_context'] = used_context
		return self._print_report(cr, uid, ids, data, context=context)
		
	def pre_print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data['form'].update(self.read(cr, uid, ids, [], context=context)[0])
		return data
		
	def _print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data = self.pre_print_report(cr, uid, ids, data, context=context)
		data['form'].update(self.read(cr, uid, ids[0]))
		if data['form']:
			date = str(data['form']['date'])
			data['form']['date_from_ind'] = self.date_indian_format(date)
			location_dest= data['form']['location_dest_id']
			loc_rec=self.pool.get('stock.location').browse(cr,uid,location_dest[0])
			location_destination=loc_rec.name
			data['form']['location']=location_destination
			
			company_id = data['form']['company_id'][0]
			com_rec = self.pool.get('res.company').browse(cr,uid, company_id)			
			data['form']['company'] = com_rec.name
			
			if data['form']['major_name']:
				stores = data['form']['major_name']
				major_rec=self.pool.get('product.category').browse(cr,uid,stores[0])
				major=major_rec.name
				data['form']['category']=major	
			return {'type': 'ir.actions.report.xml', 'report_name': 'mains.closing.stock.report', 'datas': data,  'name': 'Closing Stock'}	
		

main_closing_stock_wizard()

