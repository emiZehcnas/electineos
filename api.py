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

def connDB():
    global cur
    try:
        conn = mariadb.connect(**config)
        cur = conn.cursor()
        return True
    except mariadb.Error as e:
        stateConn = "Error: {e}"
        return False
        

def connSmart(host):
    global dev
    global plug
    try:
       dev = SmartDevice(host)
       asyncio.run(dev.update())
       
       plug = SmartPlug(host)
       asyncio.run(plug.update())
       print('okkkkk')
       return True
    except:
       print('kooooo')
       return False

    



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



@app.route('/addDevice', methods=['GET','POST'])
def addDevice():
    #Initialization of variables
    stateInsert=""
    host = request.args.get('host')
    conn = connDB()
    print(cur)
    #Connection Test
    if conn is True:
       #Connection to SmartDevice and SmartPlug
       if connSmart(host) is True:
           emeter_status = dev.emeter_realtime
           #Get the state of plug : On/Off
           if (plug.is_off):
              plugState = 'off'
           elif(plug.is_on):
              plugState = 'on'
           
           #Check if the host already exist in database
           cur.execute("SELECT host FROM devices WHERE host = '{}'".format(host)) 
           res = cur.fetchone() 
           if str(res) != "None": 
              stateInsert = "L'équipement existe déjà"
           else:
              rqt_insertDevice = "INSERT INTO ELECTINEOS.devices (alias,model,host,hardware,mac,led_state,led_state_since,plug,statut) VALUES ('{}','{}','{}','{}','{}','{}',FROM_UNIXTIME(UNIX_TIMESTAMP('{}')),'{}','{}')"
                  
              cur.execute(rqt_insertDevice.format(dev.alias,dev.model,dev.host,dev.hw_info['hw_ver'],dev.mac,plug.led,plug.on_since,plugState,'Plug disponible'))
              stateInsert = "L'insertion de l'équipement a été effectuée avec succès !"
       else:
           stateInsert ="L'équipement est introuvable"

    return stateInsert




@app.route('/removeDevice', methods=['GET','POST'])
def removeDevice():
    stateRemove=""
    iddevice = request.args.get('id')
    conn = connDB()
    if conn is True:
        try:
           req = "DELETE FROM devices WHERE id = '{}'"
           cur.execute(req.format(iddevice))
           stateRemove="l'équipement a bien été supprimé"
        except:
           stateRemove="Erreur lors de la suppression de l'équipement"
    else:
        stateRemove="Impossible de se connecter à la base de données"
    
    return stateRemove
        
                  

    


@app.route('/device', methods=['GET'])
def getDevice():
    stateConn="Connexion Ok"
    try:
        conn = mariadb.connect(**config)
        

    except mariadb.Error as e:
        stateConn = "Error: {e}"
        sys.exit(1)
    
    cur = conn.cursor()
    req = "SELECT id,alias,model,host,hardware,mac,led_state,plug,statut FROM devices"
    cur.execute(req.format())
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))


    return json.dumps(json_data)
    
    




app.run(host="0.0.0.0")
