import flask
import asyncio
import asyncclick as click
import mariadb
import json
import datetime
from kasa import SmartPlug
from kasa import SmartDevice
from pprint import pformat as pf
from flask import Flask, request
from datetime import datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True

config = {
	'host': '127.0.0.1',
	'port': 3306,
	'user': 'admin',
	'password': 'Attirasp',
	'database': 'ELECTINEOS'
}



@app.route('/off', methods=['GET'])
def stateOn():
   plug = SmartPlug('192.168.1.3')
   asyncio.run(plug.update())
   if (plug.is_on):
     asyncio.run(plug.turn_off())
     
   return request.method
   

@app.route('/on', methods=['GET'])
def stateOff():
   plug = SmartPlug('192.168.1.3')
   asyncio.run(plug.update())
   if (plug.is_off):
     asyncio.run(plug.turn_on())
     
   return request.method
   

@app.route('/deviceOld', methods=['GET'])
def scann():
   dev = SmartDevice('192.168.1.3')
   asyncio.run(dev.update())
   devs = dev.emeter_realtime
   return devs
   
   

@app.route('/alias', methods=['GET'])
def getAlias():
   dev = SmartDevice('192.168.1.3')
   asyncio.run(dev.update())
   alias = dev.alias
   
   return alias



@app.route('/data', methods=['GET'])
def data():
    stateConn="Connexion Ok"
    try:
        conn = mariadb.connect(**config)
    except mariadb.Error as e:
        stateConn = "Error: {e}"
        sys.exit(1)
    
    dev = SmartDevice ('192.168.1.3')
    asyncio.run(dev.update())
    emeter_status = dev.emeter_realtime
    
    plug = SmartPlug('192.168.1.3')
    asyncio.run(plug.update())
    
    cur = conn.cursor()
    rqt_insertDevice = "INSERT INTO ELECTINEOS.device (alias,model,host,hardware,mac,led_state,led_state_since,emeter_current,emeter_voltage,emeter_power,emeter_total_concumption,emeter_today,emeter_month) VALUES ('{}','{}','{}','{}','{}','{}',FROM_UNIXTIME(UNIX_TIMESTAMP('{}')),'{}','{}','{}','{}','{}','{}')"
    cur.execute(rqt_insertDevice.format(dev.alias,dev.model,dev.host,dev.hw_info['hw_ver'],dev.mac,plug.led,plug.on_since,emeter_status["current"],emeter_status["voltage"],emeter_status["power"],emeter_status["total"],dev.emeter_today,dev.emeter_this_month))
        
    return stateConn



@app.route('/device', methods=['GET'])
def getDevice():
    stateConn="Connexion Ok"
    try:
        conn = mariadb.connect(**config)
        

    except mariadb.Error as e:
        stateConn = "Error: {e}"
        sys.exit(1)
    
    cur = conn.cursor()
    req = "SELECT alias,model,host,hardware,mac,led_state,emeter_current,emeter_voltage,emeter_power,emeter_total_concumption,emeter_today,emeter_month FROM device"
    cur.execute(req.format())
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))


    return json.dumps(json_data)
    
    




app.run(host="0.0.0.0")
