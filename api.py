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
       
       
        

def updateDeviceByHost(host):
    stateUpdate=""
    if conn is True:
       if connSmart(host) is True:
           #Get the state of plug : On/Off
           if (plug.is_off):
              plugState = 'off'
           elif(plug.is_on):
              plugState = 'on'
           try:
              rqt_updateDevice = "UPDATE devices SET alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE host='{}' "
              cur.execute(rqt_updateDevice.format(dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'équipement disponible',datetime.now(),host))
                
              stateUpdate = "L'équipement a bien été mis à jour"
           except:
              stateUpdate = "Erreur lors de la mise à jour de l'équipement"
       else:
           try:
               rqt_updateDevice = "UPDATE devices set statut='{}',updated_at='{}' WHERE host='{}' "
               cur.execute(rqt_updateDevice.format('équipement indisponible',datetime.now(),host))
               statutUpdate = "Impossible de récupérer les données de l'équipement"
           except:
               stateUpdate = "Erreur lors de la mise à jour de l'équipement"
    else:
        statutUpdate = "Impossible de se connecter à la base de données"
           
        
    
    return stateUpdate


    



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
              rqt_insertDevice = "INSERT INTO ELECTINEOS.devices (alias,model,host,hardware,mac,led_state,plug,statut,created_at,updated_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"
                  
              cur.execute(rqt_insertDevice.format(dev.alias,dev.model,dev.host,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'Plug disponible',datetime.now(),datetime.now()))
              stateInsert = "L'insertion de l'équipement a été effectuée avec succès !"
       else:
           stateInsert ="L'équipement est introuvable"

    return stateInsert




@app.route('/removeDevice', methods=['GET','POST'])
def removeDevice():
    stateRemove=""
    idDevice = request.args.get('id')
    conn = connDB()
    if conn is True:
        try:
           #Get Host from table device by id
           req_host = "SELECT host from devices WHERE id='{}'"
           cur.execute(req_host.format(idDevice))
           field_name = [field[0] for field in cur.description]
           res = cur.fetchone()
           value = dict(zip(field_name, res))
           host = value['host']
           #delete devices row by id
           req = "DELETE FROM devices WHERE id = '{}'"
           cur.execute(req.format(idDevice))
           #delete emeter row by host
           req = "DELETE FROM emeter WHERE host = '{}'"
           cur.execute(req.format(host))
           stateRemove="l'équipement a bien été supprimé"
        except:
           stateRemove="Erreur lors de la suppression de l'équipement"
    else:
        stateRemove="Impossible de se connecter à la base de données"
    
    return stateRemove



@app.route('/updateDeviceById', methods=['GET','POST'])
def updateDeviceById():
    stateUpdate=""
    idDevice = request.args.get('id')
    conn = connDB()
    if conn is True:
       try:
           #Get Host from table device by id
           req_host = "SELECT host from devices WHERE id='{}'"
           cur.execute(req_host.format(idDevice))
           field_name = [field[0] for field in cur.description]
           res = cur.fetchone()
           value = dict(zip(field_name, res))
           host = value['host']
       except:
           stateUpdate="Erreur lors de la récupération de l'adresse IP"
       if connSmart(host) is True:
           #Get the state of plug : On/Off
           if (plug.is_off):
              plugState = 'off'
           elif(plug.is_on):
              plugState = 'on'
           try:
              rqt_updateDevice = "UPDATE devices SET alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE host='{}' "
              cur.execute(rqt_updateDevice.format(dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'équipement disponible',datetime.now(),host))
                
              stateUpdate = "L'équipement a bien été mis à jour"
           except:
              stateUpdate = "Erreur lors de la mise à jour de l'équipement"
       else:
           try:
               rqt_updateDevice = "UPDATE devices set statut='{}',updated_at='{}' WHERE host='{}' "
               cur.execute(rqt_updateDevice.format('équipement indisponible',datetime.now(),host))
               statutUpdate = "Impossible de récupérer les données de l'équipement"
           except:
               stateUpdate = "Erreur lors de la mise à jour de l'équipement"
    else:
        statutUpdate = "Impossible de se connecter à la base de données"
           
        
    
    return stateUpdate
    



@app.route('/updateAllDevices', methods=['GET'])
def updateAllDevices():
    global conn
    conn = connDB()
    if conn is True:
        req="SELECT * from devices"
        cur.execute (req.format())
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        for result in rv:
            row = dict(zip(row_headers,result))
            print(updateDeviceByHost(row['host']))
        return ("ok")
           
                
    


@app.route('/getDeviceById',methods=['GET','POST'])
def getDeviceById():
    conn = connDB()
    idDevice = request.args.get('id')
    if conn is True:
        try:
            req="SELECT * from devices WHERE id = {}"
            cur.execute (req.format(idDevice))
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
                
            return json.dumps(json_data,indent=4, sort_keys=True, default=str)
        except:                        
 
            return "Erreur lors de la récupération des données de l'équipement"        
            
            
            

@app.route('/getEmeterById', methods=['GET','POST'])
def getEmeterById():
    conn = connDB()
    idDevice = request.args.get('id')
    if conn is True:
        try:
             req = "select devices.*, emeter.* from devices INNER JOIN emeter on devices.host=emeter.host WHERE devices.id='{}' ORDER BY emeter.statement_date"
             cur.execute(req.format(idDevice))
             row_headers=[x[0] for x in cur.description]
             rv = cur.fetchall()
             json_data=[]
             for result in rv:
                 json_data.append(dict(zip(row_headers,result)))
                
             return json.dumps(json_data,indent=4, sort_keys=True, default=str)
        except:                        
 
             return "Erreur lors de la récupération des données de l'équipement"
 
 
 
@app.route('/getTotalEmeterById', methods=['GET','POST'])
def getCurrentEmeter():
    current=""
    idDevice = request.args.get('id')
    conn = connDB()
    if conn is True:
        try:
           #Get Host from table device by id
           req_host = "SELECT host from devices WHERE id='{}'"
           cur.execute(req_host.format(idDevice))
           field_name = [field[0] for field in cur.description]
           res = cur.fetchone()
           value = dict(zip(field_name, res))
           host = value['host']
           if connSmart(host) is True:
               devs = dev.emeter_realtime
               print('cest ok')
               current = str(round(devs['total'],2))
           else:
               current='ko'
        except:
           current = 'ko'
    else:
         current='ko'
    
    print(current)
    return current




@app.route('/lightSwitch',methods=['GET','POST'])
def lightSwitch():
    stateUpdate=""
    idDevice = request.args.get('id')
    conn = connDB()
    if conn is True:
        #Get Host from table device by id
        req_host = "SELECT host from devices WHERE id='{}'"
        cur.execute(req_host.format(idDevice))
        field_name = [field[0] for field in cur.description]
        res = cur.fetchone()
        value = dict(zip(field_name, res))
        host = value['host']
        if connSmart(host) is True:
            #Get the state of plug : On/Off
            if (plug.is_off):
               asyncio.run(plug.turn_on())
               plugState = 'on'
               stateUpdate = "L'équipement a bien été allumé"
            elif(plug.is_on):
               asyncio.run(plug.turn_off())
               plugState = 'off'
               stateUpdate = "L'équipement a bien été éteint"
            try:
               rqt_updateDevice = "UPDATE devices SET alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE host='{}' "
               cur.execute(rqt_updateDevice.format(dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'équipement disponible',datetime.now(),host))
            except:
               stateUpdate = "Erreur lors de la mise à jour de l'équipement"
        else:
            try:
                rqt_updateDevice = "UPDATE devices set statut='{}',updated_at='{}' WHERE host='{}' "
                cur.execute(rqt_updateDevice.format('équipement indisponible',datetime.now(),host))
                statutUpdate = "Impossible de récupérer les données de l'équipement"
            except:
                stateUpdate = "Erreur lors de la mise à jour de l'équipement"
    else:
         statutUpdate = "Impossible de se connecter à la base de données"
           
    return stateUpdate
    
        



@app.route('/test', methods=['GET','POST'])
def test():
    current=""
    idDevice = request.args.get('id')
    conn = connDB()
    if conn is True:
       #Get Host from table device by id
       req_host = "SELECT host from devices WHERE id='{}'"
       cur.execute(req_host.format(idDevice))
       field_name = [field[0] for field in cur.description]
       res = cur.fetchone()
       value = dict(zip(field_name, res))
       host = value['host']
       if connSmart(host) is True:
           devs = dev.emeter_realtime
           print('cest ok')
           current = str(devs['current'])
       else:
           current='ko'
    else:
       current='ko'
    
    print(current)
    return current
                  

    


@app.route('/device', methods=['GET'])
def getDevice():
    stateConn="Connexion Ok"
    try:
        conn = mariadb.connect(**config)
        

    except mariadb.Error as e:
        stateConn = "Error: {e}"
        sys.exit(1)
    
    cur = conn.cursor()
    req = "SELECT id,alias,model,host,hardware,mac,led_state,plug,statut,created_at,updated_at FROM devices"
    cur.execute(req.format())
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))


    return json.dumps(json_data,indent=4, sort_keys=True, default=str)
    
    




app.run(host="0.0.0.0")
