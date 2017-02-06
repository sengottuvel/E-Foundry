#!/bin/bash

py=/usr/bin/python
erp=/OpenERP/E-Foundry/openerp-server
cd $erp
nohup $py openerp-server -u kg_outwardmaster -d foundary  --db_host=localhost --db_port=5432 --no-database-list  --logfile=/OpenERP/E-Foundry/openerp-server/log/openerp-server.log &

echo "Process started successfully you can access via browser"
exit 0
