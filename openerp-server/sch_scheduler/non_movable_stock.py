import xmlrpclib

username = 'admin' #the user
pwd = 'admin'      #the password of the user
dbname = 'foundry'    #the database

# Server Connectivity

sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

## Scheduler List
sock.execute(dbname, uid, pwd, 'kg.scheduler', 'dead_stock_register_scheduler')
