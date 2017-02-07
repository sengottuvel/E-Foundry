#!/bin/bash

py=/usr/bin/python
erp=/OpenERP/E-Foundry/openerp-server
kill=/bin/kill
script=/OpenERP/E-Foundry/scripts
ps_check=`ps aux | grep openerp-server | grep -v 'grep' | grep 'foundry' | wc -l`
pid=`ps aux | grep openerp-server | grep -v 'grep' | grep 'foundry' | awk '{ print $2 }'`
echo "Process ID  $pid"
if [ $ps_check -gt 0 ]
then
echo "Old Process Running :"
$kill $pid
sleep 5
cd $script
sh openerp-start.sh
else
echo "Old Process Not Running"
cd $script
sh openerp-start.sh

echo "Old Process stopped and script started a new process"

fi

exit 1
