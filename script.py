import sys
import json
import asyncio
import mariadb
import datetime
from kasa import SmartPlug
from kasa import SmartDevice
from pprint import pformat as pf
from datetime import datetime

config = {
	'host': '127.0.0.1',
	'port': 3306,
	'user': 'admin',
	'password': 'Attirasp',
	'database': 'ELECTINEOS'
}

async def connDB():
    global cur
    try:
        conn = mariadb.connect(**config)
        cur = conn.cursor()
        return True
    except mariadb.Error as e:
        stateConn = "Error: {e}"
        return False
    
async def connSmart(host):
    global dev
    global plug
    try:
       dev = SmartDevice(host)
       await(dev.update())
       
       plug = SmartPlug(host)
       await(plug.update())
       print('okkkkk')
       return True
    except:
       print('kooooo')
       return False
              
async def emeter():
     conn = await (connDB())
     if conn is True:
         cur.execute("SELECT id,host FROM devices") 
         row_headers=[x[0] for x in cur.description]
         res = cur.fetchall()
         for row in res:
            value = dict(zip(row_headers, row))
            host = value['host']
            device=value['id']
            connex = await(connSmart(host))
            if connex is True:
                 devs = dev.emeter_realtime
                 rqt = "INSERT INTO statements (host,statement_date,emeter_current,emeter_voltage,emeter_power,emeter_total_concumption,emeter_today,emeter_month,device) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')"
                 cur.execute(rqt.format(host,datetime.now(),devs["current"],devs["voltage"],devs["power"],devs["total"],dev.emeter_today,dev.emeter_this_month,device))
                 print(devs['current'])
                 print(devs['voltage'])
                 print(devs['power'])
                 print(devs['total'])
            else:
                print('ko')
     else:
         print("ko")                   
      

asyncio.run(emeter())                        