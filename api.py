import flask
import asyncio
import asyncclick as click
import mariadb
import json
import datetime
import logging
from kasa import SmartPlug
from kasa import SmartDevice
from pprint import pformat as pf
from flask import Flask, request
from datetime import datetime
from datetime import date
from pprint import pprint

app = flask.Flask(__name__)
app.config["DEBUG"] = True

logging.basicConfig(filename=str(date.today())+'.log', level=logging.INFO)

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
        logging.info('Connexion à la base de données')
        return True
    except mariadb.Error as e:
        logging.error('Echec lors de la connexion à la base de données : {e}')
        return False
        

def connSmart(host):
    global dev
    global plug
    try:
       dev = SmartDevice(host)
       asyncio.run(dev.update())
       
       plug = SmartPlug(host)
       asyncio.run(plug.update())
       logging.info('Récupération de la configuration de l\'équipement')
       return True
    except:
       logging.error('Echec lors de la récupération de la configuration de l\'équipement')
       return False
       
       
        

def updateDeviceByHost(host,idDevice):
    stateUpdate=""
    if connDB() is True:
       if connSmart(host) is True:
           #Get the state of plug : On/Off
           if (plug.is_off):
              plugState = 'off'
           elif(plug.is_on):
              plugState = 'on'
           try:
              rqt_updateDevice = "UPDATE devices SET host='{}', alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE id='{}' "
              cur.execute(rqt_updateDevice.format(host,dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'équipement disponible',datetime.now(),idDevice))
                
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




def getHost(idDevice):
    if connDB() is True:
           try:
              rqt = "SELECT host from devices WHERE id='{}'"
              cur.execute(rqt.format(idDevice))
              field_name = [field[0] for field in cur.description]
              res = cur.fetchone()
              value = dict(zip(field_name, res))
              host = value['host']
              logging.info("récupération de l'adresse IP "+host)
           except:
              host="0000"
              logging.error("getHost : Impossible de récupérer l'adresse IP")
    return host
    



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



@app.route('/device/add', methods=['GET','POST'])
def deviceAdd():
    #Initialization of variables
    status=""
    host = request.args.get('host') 
    print(cur)
    #Connection Test
    if connDB() is True:
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
              status = "L'équipement existe déjà"
           else:
              try:
                  rqt = "INSERT INTO ELECTINEOS.devices (alias,model,host,hardware,mac,led_state,plug,statut,created_at,updated_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"    
                  cur.execute(rqt.format(dev.alias,dev.model,dev.host,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'Plug disponible',datetime.now(),datetime.now()))
                  status = "L'insertion de l'équipement a été effectuée avec succès !"
                  logging.info('deviceAdd : L\'insertion de l\'équipement : '+ host)
              except:
                  status = "Erreur lors de l'insertion de l'équipement"
                  logging.error('deviceAdd : Erreur lors de l\'insertion de l\'équipement : '+ host)
       else:
           status ="L'équipement est introuvable"
           logging.warning('deviceAdd : L\'équipement est introuvable')
    else:
       status: "Impossible de se connecter à la base de données"
       logging.warning('deviceAdd : Impossible de connecter à la base de données')

    return status




@app.route('/device/remove', methods=['GET','POST'])
def deviceRemove():
    status=""
    idDevice = request.args.get('id') 
    if connDB() is True:
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
           status="l'équipement a bien été supprimé"
           logging.info('Suppression de l\'équipement')
        except:
           status="Erreur lors de la suppression de l'équipement"
           logging.error('deviceRemove : Erreur lors de la suppression de l\'équipement')
           
    else:
        status="Impossible de se connecter à la base de données"
        logging.warning('deviceRemove : Impossible de connecter à la base de données')
    
    return status



@app.route('/device/update', methods=['GET','POST'])
def deviceUpdate():
    response =""
    if request.method == 'GET':
        idDevice = request.args.get('id')
        if connDB() is True:
           try:
               #Get Host from table device by id
               rqt = "SELECT host from devices WHERE id='{}'"
               cur.execute(rqt.format(idDevice))
               field_name = [field[0] for field in cur.description]
               res = cur.fetchone()
               value = dict(zip(field_name, res))
               host = value['host']
               status = updateDeviceByHost(host,idDevice)
               logging.info('deviceUpdate : Mise à jour de L\'équipement')
           except:
               response  ="Erreur lors de la mise à jour de l'équipement"
               logging.error('deviceUpdate : Erreur lors de la mise à jour de l\'équipement')
        else:
           response ="Impossible de se connecter à la base de données"
           logging.warning('deviceRemove : Impossible de connecter à la base de données')
    elif request.method =='POST':
        host = request.form['host']
        idDevice = request.form['idDevice']
        response = updateDeviceByHost(host,idDevice)

    return response
    



@app.route('/devices/update', methods=['GET'])
def devicesUpdate():
    if connDB() is True:
        req="SELECT * from devices"
        cur.execute (req.format())
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        for result in rv:
            row = dict(zip(row_headers,result))
            print(updateDeviceByHost(row['host'],row['id']))
        Status ="Tous les équipements ont été mis à jour dans la base de données"
        return Status
           
                
    


@app.route('/device',methods=['GET'])
def device():
    idDevice = request.args.get('id')
    response =""
    if connDB() is True:
        try:
            req="SELECT * from devices WHERE id = {}"
            cur.execute (req.format(idDevice))
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
                
            response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
        except:                        
            response = "Erreur lors de la récupération des données de l'équipement"
    else:
        response = "Erreur lors de la connexion à la base de données"
    return response        
            
            
            

@app.route('/emeter', methods=['GET','POST'])
def emeter():
    _id = request.args.get('id')
    _filter  = request.args.get('filter')
    response=""
    if connDB() is True:
        try:
            if _filter == "month":
                req = "select devices.*, emeter.id, emeter.host, UNIX_TIMESTAMP(emeter.statement_date) as statement_date, emeter.emeter_current, emeter.emeter_voltage, emeter.emeter_power, emeter.emeter_total_concumption, emeter.emeter_today, emeter_month from devices INNER JOIN emeter on devices.host=emeter.host WHERE devices.id='{}' AND MONTH(emeter.statement_date) = MONTH(CURRENT_DATE()) ORDER BY emeter.statement_date DESC"
                #req = "select devices.*, emeter.id, emeter.host, UNIX_TIMESTAMP(emeter.statement_date) as statement_date, emeter.emeter_current, emeter.emeter_voltage, emeter.emeter_power, emeter.emeter_total_concumption, emeter.emeter_today, emeter_month from devices INNER JOIN emeter on devices.host=emeter.host WHERE devices.id='{}' ORDER BY emeter.statement_date DESC"

            elif _filter == "all":
                req = "select emeter.statement_date as 'Date relevé', emeter.emeter_today as 'Moyenne par jour', emeter.emeter_month as 'Moyenne par mois', emeter.emeter_total_concumption as 'Moyenne totale' from devices INNER JOIN emeter on devices.host=emeter.host WHERE devices.id='{}' ORDER BY emeter.statement_date DESC"
            cur.execute(req.format(_id))
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
                
            response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
        except:                        
             response = "Erreur lors de la récupération des données de l'équipement"
    else:
        response = "Impossible de se connecter à la base de données"
    
    return response
 
 
 
@app.route('/emeter/total', methods=['GET','POST'])
def emeterTotal():
    response ="0.00"
    idDevice = request.args.get('id')
    if connDB() is True:
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
               response = str(round(devs['total'],2))
           else:
               logging.error(" emeterTotal() : Impossible de se connecter à l'équipement.")
        except:
           logging.error('emeterTotal() : Erreur')
    else:
         logging.warning('Impossible de se connecter à la base de données.')
    
    #print(response)
    return response




@app.route('/lightSwitch',methods=['GET'])
def lightSwitch():
    response=""
    idDevice = request.args.get('id')
    if connDB() is True:
        try:
            host = getHost(idDevice)
            print (host)
            if connSmart(host) is True:
                #Get the state of plug : On/Off
                print("conn smart ok")
                if (plug.is_off):
                   asyncio.run(plug.turn_on())
                   plugState = 'on'
                   response = "L'équipement a bien été allumé"
                elif(plug.is_on):
                   asyncio.run(plug.turn_off())
                   plugState = 'off'
                   response = "L'équipement a bien été éteint"
                rqt = "UPDATE devices SET alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE host='{}' "
                cur.execute(rqt.format(dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,'équipement disponible',datetime.now(),host))
            else:
                rqt = "UPDATE devices set statut='{}',updated_at='{}' WHERE host='{}' "
                cur.execute(rqt.format('équipement indisponible',datetime.now(),host))
                response = "Impossible de récupérer les données de l'équipement"
        except:
            response = ""
        
    else:
         response = "Impossible de se connecter à la base de données"
           
    return response




@app.route('/scheduling/all', methods=['GET','POST'])
def allScheduling():
    response =""
    idDevice = request.args.get('id')
    if connDB() is True:
       try:
           rqt = "SELECT * FROM schedules WHERE device='{}' ORDER BY timeScheduling ASC"
           cur.execute(rqt.format(idDevice))
           row_headers=[x[0] for x in cur.description]
           rv = cur.fetchall()
           json_data=[]
           for result in rv:
               json_data.append(dict(zip(row_headers,result)))
           response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
           logging.info('schedules : Récupération des tâches planifiées')
       except:
           response ="Erreur lors de la récupération des tâches planifiées"
           logging.error('schedules : Erreur lors de la mise à jour de l\'équipement')
    else:
       response ="Impossible de se connecter à la base de données"
       logging.warning('scheduling : Impossible de connecter à la base de données')

    return response
    
        


@app.route('/scheduling', methods=['POST','DELETE','GET','PUT'])
def scheduling():
    response =""
    upd =0
    value=""
    _action=""
    maxId=0
    if request.method=='POST':         
        idDevice = request.form['idDevice']
        action = request.form['display_on_dashboard']
        time = request.form['time_scheduling']
        isActive = request.form['isActive']
        data  = json.loads('{"days": '+request.form.getlist('days')[0]+'}')
        if connDB() is True:
           try:
              #host = getHost(idDevice)
              #Insertion de la ligne dans la table
              rqt = "insert into schedules(device,actionScheduling,timeScheduling,isActive) VALUES('{}','{}','{}','{}')"
              cur.execute(rqt.format(idDevice,action,time,isActive))
              #select last row insered by id
              rqt = "SELECT max(id) as maxId from schedules"
              cur.execute(rqt.format())
              field_name = [field[0] for field in cur.description]
              res = cur.fetchone()
              value = dict(zip(field_name, res))
              maxId = value['maxId']
              print(maxId) 
              for item in data['days']:
                 #Control existing plannification at the same day and time
                 rqt = "SELECT * FROM schedules WHERE {}=1 AND timeScheduling='{}'"
                 cur.execute(rqt.format(item,time))
                 res = cur.fetchone() 
                 if str(res) == "None": 
                     upd += 1
                     rqt = "UPDATE schedules SET {}=1 WHERE id={}"
                     cur.execute(rqt.format(item,maxId))
                     print(rqt.format(item,maxId))
                 #daySelected.append(day)
              if upd == 0:
                  rqt = "DELETE FROM schedules WHERE id={}"
                  cur.execute(rqt.format(maxId))
                  response ="Planifications non effectuée pour cause de doublons."
              else:
                  response ="Planification effectuée."
           except:
               response ="Scheduling : Erreur lors de l'insertion de la tâche planifiée"
               logging.error("scheduling -> POST : Erreur lors de l'insertion de la tâche planifiée")
    elif request.method =='DELETE':
        if connDB() is True:
            try:
                _id = request.form['idScheduling']
                print("id "+str(_id))
                rqt = "DELETE FROM schedules WHERE id={}"
                cur.execute(rqt.format(_id))
                response = "Suppression de la tâche planifiées."
                logging.info("Suppression de la tâche planifiée "+_id)
            except:
                response="Erreur lors de la suppression de la tâche planifiée"
                logging.error("Scheduling -> DELETE : Error lors de la suppression de la tâche planifiée "+_id)
        else:
            response="Erreur lors de la connection à la base de données"
            logging.warning("scheduling -> DELETE : Erreur de connexion à la base de donnée")
    #print('jsonload : '+str(data['days'])) 
    #print(request.form.getlist('days'))
    elif request.method =='GET':
        if connDB() is True:
            try:
                idScheduling = request.args.get('id')
                rqt = "SELECT * FROM schedules WHERE id={}"
                cur.execute(rqt.format(idScheduling))
                row_headers=[x[0] for x in cur.description]
                rv = cur.fetchall()
                json_data=[]
                for result in rv:
                    json_data.append(dict(zip(row_headers,result)))
                
                response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
            except:
                response ="Erreur lors de la récupération de la tâche planifiée."
                logging.error("scheduling -> GET : Erreur lors de la récupération de la tpache planifiée")
    elif request.method =='PUT':
        if connDB():
            idScheduling = request.form['idScheduling']
            action = request.form['display_on_dashboard']
            time = request.form['time_scheduling']
            isActive = request.form['isActive']
            data  = json.loads('{"days": '+request.form.getlist('days')[0]+'}')
            rqt="UPDATE schedules set actionScheduling={}, timeScheduling='{}',isActive={}, monday=0, tuesday=0, wednesday=0, thursday=0, friday=0, saturday=0, sunday=0 WHERE id={}"
            cur.execute(rqt.format(action,time,isActive,idScheduling))
            for item in data['days']:
                 #Control existing plannification at the same day and time
                 rqt = "SELECT * FROM schedules WHERE {}=1 AND timeScheduling='{}'"
                 cur.execute(rqt.format(item,time))
                 res = cur.fetchone() 
                 if str(res) == "None": 
                     upd += 1
                     rqt = "UPDATE schedules SET {}=1 WHERE id={} "
                     cur.execute(rqt.format(item,idScheduling))
                     print(rqt.format(item,idScheduling))
            if upd == 0:
                rqt = "DELETE FROM schedules WHERE id={}"
                cur.execute(rqt.format(idScheduling))
                response ="Planifications non effectuée pour cause de doublons."
            else:
                response ="Planification effectuée."
            
        else:
            response="Erreur lors de la connection à la base de données"
            logging.warning("scheduling -> PUT : Erreur de connexion à la base de donnée")
    
    return response
                
                
    



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
                  

    


@app.route('/devices')
def devices():
    stateConn=""
    req = "SELECT id,alias,model,host,hardware,mac,led_state,plug,statut,created_at,updated_at FROM devices"
    if connDB() is True:
            cur.execute(req.format())
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))

            response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
    else:
        response = "Impossible de se connecter à la base de données."
        logging.warning("devices -> Impossible de se connecter à la base de données.")
    return response
  
    
    




app.run(host="0.0.0.0")
