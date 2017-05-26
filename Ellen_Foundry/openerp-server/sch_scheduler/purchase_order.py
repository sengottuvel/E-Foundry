import xmlrpclib

username = 'admin' #the user
pwd = 'admin'      #the password of the user
dbname = 'ellen_fc'    #the database

# Server Connectivity

sock_common = xmlrpclib.ServerProxy ('http://localhost:8072/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://localhost:8072/xmlrpc/object')

## Scheduler List
sock.execute(dbname, uid, pwd, 'kg.scheduler', 'daily_purchase_order_mail')
