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

logging.basicConfig(filename='/home/pi/api/log/'+str(date.today())+'_api.log', level=logging.INFO)

config = {
	'host': '127.0.0.1',
	'port': 3306,
	'user': 'admin',
	'password': 'Attirasp',
	'database': 'ELECTINEOS'
}

def connDB():
    ''' Connexion à la base de données
        Cette fontion permet de se connecter à la base de données
    Args:
    Returns:
        boolean
    '''
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
    ''' Connection à l'équipement
    
        Cette fonction permet de se connecter à l'équipement.
    Args:
        host
    Returns:
        boolean
    '''
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
    ''' Mise à jour de l'équipement
       Cette fonction permet de mettre à jour un équipement
       
    Args:
        host, idDevice
    Returns:
        status
    '''
    #Initialisaton des variables
    status =""
    #Connection à la base de données
    if connDB() is True:
       try:
           #Connection à l'équipement
           if connSmart(host) is True:
               if (plug.is_off):
                  plugState = 'off'
               elif(plug.is_on):
                  plugState = 'on'
               rqt = "UPDATE devices SET host='{}', alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE id='{}' "
               cur.execute(rqt.format(host,dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,1,datetime.now(),idDevice))
                
               status = "L'équipement a bien été mis à jour"
               logging.info("---- updateDeviceByHost() : Equipement mise à jour")
           else:
               rqt = "UPDATE devices set statut='{}',updated_at='{}' WHERE host='{}' "
               cur.execute(rqt.format(2,datetime.now(),host))
               logging.warning("---- updateDeviceByHost() : Equipement indisponible")
               status = "Equipement indisponible"
       except:
           logging.error("---- updateDeviceByHost() : Erreur lors de la mise à jour de l'équipement")
           status = "Erreur lors de la mise à jour de l'équipement"
    else:
        status = "Impossible de se connecter à la base de données"
        logging.warning('---- updateDeviceByHost() : Impossible de connecter à la base de données ----')
               
    
    return status




def getHost(idDevice):
    ''' Cette fonction permet de récupérer l'adresse ip à partir de l'id de l'équipement
    Args:
        idDevice
    Returns:
        host
    '''
    #Connection à la base de données
    if connDB() is True:
           try:
              #Récupération de l'adresse IP
              rqt = "SELECT host from devices WHERE id='{}'"
              cur.execute(rqt.format(idDevice))
              field_name = [field[0] for field in cur.description]
              res = cur.fetchone()
              value = dict(zip(field_name, res))
              host = value['host']
              logging.info("---- getHost() :récupération de l'adresse IP "+host+" ----")
           except:
              host="0000"
              logging.error("---- getHost() : Impossible de récupérer l'adresse IP"+ " ----")
    return host
    



@app.route ('/')
def response():
    return "ok"



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



@app.route('/device/add', methods=['GET'])
def deviceAdd():
    ''' Ajoute un équipement à partir de son adresse IP :
    
        Cette fonction permet d'insérer en base de données un équipement en récupérant l'adresse IP via une méthode GET.
        La connection à un équipement s'effectue via l'API Kasa
    
    Args :
     
    Methods :
        GET
    Returns :
        response
     '''
    #Initialisation des variables.
    response =""
    host = request.args.get('host') 
    if connDB() is True:
       try:
           #Connection à l'équipement 
           if connSmart(host) is True:
               emeter_status = dev.emeter_realtime
               #Récupération de l'état de l'équipement : on/off
               if (plug.is_off):
                  plugState = 'off'
               elif(plug.is_on):
                  plugState = 'on'         
               #Vérification de l'équipement dans la table "devices"
               logging.info("---- deviceAdd() : Vérification de l'existance de l'équipement "+" ----")
               cur.execute("SELECT host FROM devices WHERE host = '{}'".format(host)) 
               res = cur.fetchone() 
               if str(res) != "None": 
                   response = "L'équipement existe déjà"
                   logging.info("---- deviceAdd() : L'équipement existe déjà ----")
               else:
                   #Insertion de l'équipement en base de données.
                   rqt = "INSERT INTO ELECTINEOS.devices (alias,model,host,hardware,mac,led_state,plug,statut,created_at,updated_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"    
                   cur.execute(rqt.format(dev.alias,dev.model,dev.host,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,1,datetime.now(),datetime.now()))
                   response = "L'insertion de l'équipement a été effectuée avec succès !"
                   logging.info("---- deviceAdd() : L\'insertion de l\'équipement : "+ host+" ----")
           else:
               #Si la connection à l'équipement à échouée
               response ="L'équipement est introuvable"
               logging.warning("---- deviceAdd() : L'équipement est introuvable ----")
       except:
           response="Erreur lors de l'insert de l'équipement"
           logging.error("---- deviceAdd() : Erreur lors de l'insertion de l'équipement ----")
    else:
       response: "Impossible de se connecter à la base de données"
       logging.warning('---- deviceAdd() : Impossible de connecter à la base de données ----')

    return response




@app.route('/device/remove', methods=['GET'])
def deviceRemove():
    ''' Suppression d'un équipement.
    
        Cette fonction permet de supprimer un équipement.
    
    *** Suppression dans la table "statements"
    *** Suppression dans la table "schedules"
    *** Suppression dans la table "devices"
    
    Args:
    Methods:
        GET
    Returns:
        response
    '''
    #Initialisation des variables
    response =""
    idDevice = request.args.get('id') 
    if connDB() is True:
        try:
           #Suppression dans la table statements
           req = "DELETE FROM statements WHERE device = '{}'"
           cur.execute(req.format(idDevice))
           #Suppression dans la table schedules
           req = "DELETE FROM schedules WHERE device = '{}'"
           cur.execute(req.format(idDevice))
           #Suppression dans la table devices
           req = "DELETE FROM devices WHERE id = '{}'"
           cur.execute(req.format(idDevice))
           response="l'équipement a bien été supprimé"
           logging.info("---- deviceRemove() : Suppression de l'équipement ----")
        except:
           response="Erreur lors de la suppression de l'équipement"
           logging.error("---- deviceRemove() : Erreur lors de la suppression de l'équipement ----")          
    else:
        response="Impossible de se connecter à la base de données"
        logging.warning("---- deviceRemove() : Impossible de connecter à la base de données ----")
    
    return response



@app.route('/device/update', methods=['GET','PUT'])
def deviceUpdate():
    ''' Mise à jour de l'équipement
    
        Cette fonction permet de mettre à jour l'équipement.
    
        Mise à jour avec l'id de l'équipement si l'ip de l'équipement n'a pas changé.
        Mise à jour avec l'Adresse IP de l'équipement via un formulaire de saisie si l'IP de l'équipement à changé.
    Args:
    Methods:
        GET,PUT
    Returns :
        response
    '''
    #Initialisation des variables
    response =""
    if request.method == 'GET':
        idDevice = request.args.get('id')
        if connDB() is True:
           try:
               #Récupère l'adresse ip grace à l'id
               rqt = "SELECT host from devices WHERE id='{}'"
               cur.execute(rqt.format(idDevice))
               field_name = [field[0] for field in cur.description]
               res = cur.fetchone()
               value = dict(zip(field_name, res))
               host = value['host']
               response = updateDeviceByHost(host,idDevice)
               logging.info("---- deviceUpdate() : Mise à jour de L'équipement ----")
           except:
               response  ="Erreur lors de la mise à jour de l'équipement"
               logging.error("---- deviceUpdate() : Erreur lors de la mise à jour de l'équipement ----")
        else:
           response ="Impossible de se connecter à la base de données"
           logging.warning("---- deviceUpdate() : Impossible de connecter à la base de données ----")
    elif request.method =='PUT':
        host = request.form['host']
        idDevice = request.form['idDevice']
        response = updateDeviceByHost(host,idDevice)

    return response
    



@app.route('/devices/update', methods=['GET'])
def devicesUpdate():
    ''' Mise à jour de tous les équipements 
        Cette fonction permet de mettre à jour tous les équipements de la base de données.
    Args:
    Methods:
       GET
    Returns:
       response
    '''
    #Initialisation des variables
    response =""
    if connDB() is True:
        try:
            #Récupération de tous les équipements
            req="SELECT * from devices"
            cur.execute (req.format())
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            for result in rv:
               row = dict(zip(row_headers,result))
               #Mise à jour de chaque équipement.
               updateDeviceByHost(row['host'],row['id'])
            response ="Tous les équipements ont été mis à jour dans la base de données"
            logging.info("---- devicesUpdate() : Tous les équipements ont été mis à jour dans la base de données ----")
        except:
            response ="Erreur lors de la mise à jour des équipements"
            logging.error("---- devicesUpdate() : Erreur lors de la mise à jour des équipements ----")
    else:
        response="Erreur de connexion à la base de données"
        logging.warning("---- devicesUpdate() : Impossible de se connecter à la base de données ----")
        
    return response
           
               
    


@app.route('/device',methods=['GET'])
def device():
    ''' Récupération de l'équipement
    
        Cette fonction permet de récupérer les informations de l'équipement à l'aide de l'id
    Args:
    Methods:
        GET
    Returns:
        response
    '''
    #Initialisation des variables
    idDevice = request.args.get('id')
    response =""
    #Connection à la base de données
    if connDB() is True:
        try:
            req="SELECT devices.id,alias,model,host,hardware,mac,led_state,led_state_since,plug,status.status as statut,created_at,updated_at FROM devices left join status on devices.statut = status.id WHERE devices.id = {}"
            cur.execute (req.format(idDevice))
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            #Stockage en JSON du résultat de la requête
            for result in rv:
                value = dict(zip(row_headers, result))
                json_data.append(dict(zip(row_headers,result)))
                logging.info("---- device() : Récupération des données de l'équipement : "+value['alias']+" ----")
                
            response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
        except:                        
            response = "Erreur lors de la récupération des informations de l'équipement"
            logging.error("---- device() : Erreur lors de la récupération des données de l'équipement ----")
    else:
        response = "Erreur lors de la connexion à la base de données"
        logging.warning("---- device() : Impossible de se connecter à la base de données ----")
    return response        
            
            
            

@app.route('/emeter', methods=['GET'])
def emeter():
    ''' Récupération du relevé de consommation
        Cette fonction permet de récupérer le relevé de consommation d'un équipement de la table "statements"
    Args:
    Methods:
        GET
    Returns:
       response
    '''
    #Initialisation des variables
    _id = request.args.get('id')
    _filter  = request.args.get('filter')
    response=""
    req=""
    if connDB() is True:
        try:
            #récupération des données par mois
            if _filter == "month":
                req = "select devices.*, statements.id, statements.host, UNIX_TIMESTAMP(statements.statement_date) as statement_date, statements.emeter_current, statements.emeter_voltage, statements.emeter_power, statements.emeter_total_concumption, statements.emeter_today, statements.emeter_month from devices INNER JOIN statements on devices.id=statements.device WHERE devices.id='{}' AND MONTH(statements.statement_date) = MONTH(CURRENT_DATE()) ORDER BY statements.statement_date DESC"
                #req = "select devices.*, emeter.id, emeter.host, UNIX_TIMESTAMP(emeter.statement_date) as statement_date, emeter.emeter_current, emeter.emeter_voltage, emeter.emeter_power, emeter.emeter_total_concumption, emeter.emeter_today, emeter_month from devices INNER JOIN emeter on devices.host=emeter.host WHERE devices.id='{}' ORDER BY emeter.statement_date DESC"
                logging.info("---- emeter() : Relevé par device ----")
            #récupération de toutes les données
            elif _filter == "all":
                req = "select devices.alias, statements.statement_date as 'Date relevé', statements.emeter_today as 'Moyenne par jour', statements.emeter_month as 'Moyenne par mois', statements.emeter_total_concumption as 'Moyenne totale' from devices INNER JOIN statements on devices.id=statements.device WHERE devices.id='{}' ORDER BY statements.statement_date DESC"
                logging.info("emeter() : Récupération pour tout les relevés.")
            cur.execute(req.format(_id))
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            #Stockage en JSON du résultat de la requête
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
                
            response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
            logging.info("---- emeter() : Récupération du relevé ----")
        except:                        
             response = "Erreur lors de la récupération des données de l'équipement"
             logging.error("---- emeter() : Erreur lors de la récupération du relevé ----")
    else:
        response = "Impossible de se connecter à la base de données"
        logging.warning("---- emeter() : Impossible de se connecter à la base de données ----")
    
    return response
 
 
 
@app.route('/emeter/total', methods=['GET'])
def emeterTotal():
    ''' Récupération de la consommation en temps réel
        Cette fonction pemet de récupérer la consommation en temps réel en KwH de l'équipement
    Args:
    Methods:
        GET
    Return:
        Response
    '''
    #Initialisation des variables
    response ="0.00"
    idDevice = request.args.get('id')
    if connDB() is True:
        try:
           #Récupération de l'adresse IP à l'aide de l'ID
           req_host = "SELECT host,alias from devices WHERE id='{}'"
           cur.execute(req_host.format(idDevice))
           field_name = [field[0] for field in cur.description]
           res = cur.fetchone()
           value = dict(zip(field_name, res))
           host = value['host']
           if connSmart(host) is True:
               #Récupération de la consommation en temps réel
               devs = dev.emeter_realtime
               response = str(round(devs['total'],2))
               logging.info("---- emeterTotal() : Récupération de la consommation totale de l'équipement : "+value['alias']+" ----")
           else:
               logging.warning("---- emeterTotal() : Impossible de récupérer la consommation totale de l'équipement : "+value['alias']+" ----")
        except:
           logging.error("---- emeterTotal() : Erreur lors de la récupération de la cosonsommation totale de l'équipement"+" ----")
    else:
         logging.warning("---- emeterTotal() : Impossible de se connecter à la base de données"+ " ----")
    
    return response




@app.route('/lightSwitch',methods=['GET'])
def lightSwitch():
    ''' Activiation et desactivation de l'équipement
     
        Cette fonction permet d'activer ou de desactiver l'équipement
    Args:
    Methods:
        GET
    Returns:
       Response
    '''
    #Initialisation des variables
    response=""
    idDevice = request.args.get('id')
    if connDB() is True:
        try:
            host = getHost(idDevice)
            #Connection à l'équipement
            if connSmart(host) is True:
                #Si l'équipement est désactivé, alors l'activer
                if (plug.is_off):
                   asyncio.run(plug.turn_on())
                   plugState = 'on'
                   response = "L'équipement a bien été allumé"
                #Si l'équipement est activé, alors le desactivé
                elif(plug.is_on):
                   asyncio.run(plug.turn_off())
                   plugState = 'off'
                   response = "L'équipement a bien été éteint"
                #Mise à jour de l"équipement
                rqt = "UPDATE devices SET alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE host='{}' "
                cur.execute(rqt.format(dev.alias,dev.model,dev.hw_info['hw_ver'],dev.mac,plug.led,plugState,1,datetime.now(),host))
            else:
                rqt = "UPDATE devices set statut='{}',updated_at='{}' WHERE host='{}' "
                cur.execute(rqt.format(2,datetime.now(),host))
                response = "Impossible de récupérer les données de l'équipement"
        except:
            response = ""
        
    else:
         response = "Impossible de se connecter à la base de données"
           
    return response




@app.route('/scheduling/all', methods=['GET'])
def allScheduling():
    ''' Récupération de tous les équipements
     
        Cette fonction permet de récupérer toutes les planifications
    Args:
    Methods:
        GET
    Returns:
        response
    '''
    #Initialisation des variables
    response =""
    idDevice = request.args.get('id')
    #Connection à la base de données
    if connDB() is True:
       try:
           rqt = "SELECT * FROM schedules WHERE device='{}' ORDER BY timeScheduling ASC"
           cur.execute(rqt.format(idDevice))
           row_headers=[x[0] for x in cur.description]
           rv = cur.fetchall()
           json_data=[]
           #Stockage en JSON du résultat de la requête
           for result in rv:
               json_data.append(dict(zip(row_headers,result)))
           response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
           logging.info("---- allScheduling() : Récupération des tâches planifiées ----")
       except:
           response ="Erreur lors de la récupération des tâches planifiées"
           logging.error("---- allScheduling() : Erreur lors de la mise à jour de l\'équipement ----")
    else:
       response ="Impossible de se connecter à la base de données"
       logging.warning("---- allScheduling() : Impossible de connecter à la base de données ----")

    return response
    
        


@app.route('/scheduling', methods=['POST','DELETE','GET','PUT'])
def scheduling():
    ''' Planifications
    
        Cette fonction permet d'inserer, supprimer, récupérer et modifier une planification.
    
        Methode POST : Insertion d'une planification via les données d'un formulaire.
        Methode DELETE : Suppression d'une planification
        Methode GET : Récupération d'une planification pour l'afficher dans un formulaire
        Methode PUT : Modification d'une planification
        
    Args:
    Methods:
        POST, GET, DELETE, PUT
    Returns:
        response
    '''
    #Initialisation des variables communes
    response =""
    upd =0
    value=""
    _action=""
    maxId=0
    if request.method=='POST':
        logging.info("---- scheduling/POST : Méthode POST  ----")  
        #Récupération des variables du formulaire      
        idDevice = request.form['idDevice']
        action = request.form['display_on_dashboard']
        time = request.form['time_scheduling']
        isActive = request.form['isActive']
        data  = json.loads('{"days": '+request.form.getlist('days')[0]+'}')
        print(data['days'])
        #connection à la base de données
        if connDB() is True:
           try:
              #host = getHost(idDevice)
              #Insertion de la planification dans la table (sauf les jours)
              rqt = "insert into schedules(device,actionScheduling,timeScheduling,isActive) VALUES('{}','{}','{}','{}')"
              cur.execute(rqt.format(idDevice,action,time,isActive))
              logging.info("---- scheduling/POST : Insertion de la planification en base de données  ----")
              #Récupération de l'id de la dernière planification inserée
              rqt = "SELECT max(id) as maxId from schedules"
              cur.execute(rqt.format())
              field_name = [field[0] for field in cur.description]
              res = cur.fetchone()
              value = dict(zip(field_name, res))
              maxId = value['maxId']
              logging.info("---- scheduling/POST : Vérification si d'autre planifications sont prévues aux mêmes heures  ----") 
              for item in data['days']:
                 #Vérification si une enregistrement existe pour un même jour et la même heure
                 rqt = "SELECT * FROM schedules WHERE {}=1 AND timeScheduling='{}'"
                 cur.execute(rqt.format(item,time))
                 res = cur.fetchone() 
                 if str(res) == "None": 
                     upd += 1
                     #Activiation en mettant à jour la valeur true le jour concerné.
                     rqt = "UPDATE schedules SET {}=1 WHERE id={}"
                     cur.execute(rqt.format(item,maxId))
                     print(rqt.format(item,maxId))
                 logging.info("---- scheduling/POST : Ajout des jours sélectionnés pour la planification  ----")
              if upd == 0:
                  #Si aucun jour n'a été activés, suppression de la ligne.
                  rqt = "DELETE FROM schedules WHERE id={}"
                  cur.execute(rqt.format(maxId))
                  response ="Planifications non effectuée pour cause de doublons."
                  logging.info("---- scheduling/POST : La planification a été supprimée pour cause de doublons  ----")
              else:
                  response ="Planification effectuée"
                  logging.info("---- scheduling/POST : Ajout de la planification  ----")
           except:
               response ="Scheduling : Erreur lors de l'insertion de la tâche planifiée"
               logging.error("---- scheduling/POST : Erreur lors de l'insertion de la planification ----")
    elif request.method =='DELETE':
        logging.info("---- scheduling/DELETE : Méthode DELETE  ----")
        #connection à la base de données
        if connDB() is True:
            try:
                #Initialisation des variables
                _id = request.form['idScheduling']
                #Suppression de la planification
                rqt = "DELETE FROM schedules WHERE id={}"
                cur.execute(rqt.format(_id))
                response = "Suppression de la tâche planifiées."
                logging.info("---- scheduling/DELETE : Suppression de la planification "+_id+" ----")
            except:
                response="Erreur lors de la suppression de la tâche planifiée"
                logging.error("---- Scheduling/DELETE : Error lors de la suppression de la planification "+_id+" ----")
        else:
            response="Erreur lors de la connection à la base de données"
            logging.warning("---- scheduling/DELETE : Erreur de connexion à la base de donnée ----")
    elif request.method =='GET':
        logging.info("---- scheduling/GET : Méthode GET  ----")
        #Connection à la base de données
        if connDB() is True:
            try:
                #Initialisation des variables
                _id = request.args.get('id')
                rqt = "SELECT * FROM schedules WHERE id={}"
                cur.execute(rqt.format(_id))
                row_headers=[x[0] for x in cur.description]
                rv = cur.fetchall()
                json_data=[]
                #Stoackage des données au format JSON
                for result in rv:
                    json_data.append(dict(zip(row_headers,result)))
                
                response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
                logging.info("---- scheduling/GET : Récupération de la planification "+_id+" ----")
            except:
                response ="Erreur lors de la récupération de la tâche planifiée."
                logging.error("scheduling/GET : Erreur lors de la récupération de la tpache planifiée")
    elif request.method =='PUT':
        logging.info("---- scheduling/PUT : Méthode PUT  ----")
        #Connection à la base de données
        if connDB():
            #Initialisation des variables
            idScheduling = request.form['idScheduling']
            action = request.form['display_on_dashboard']
            time = request.form['time_scheduling']
            isActive = request.form['isActive']
            data  = json.loads('{"days": '+request.form.getlist('days')[0]+'}')
            #Mise à 0 tous les jours de la semaine pour la planification
            rqt="UPDATE schedules set actionScheduling={}, timeScheduling='{}',isActive={}, monday=0, tuesday=0, wednesday=0, thursday=0, friday=0, saturday=0, sunday=0 WHERE id={}"
            cur.execute(rqt.format(action,time,isActive,idScheduling))
            logging.info("---- scheduling/PUT : Mise à jour de la planification et remise à zéro des jours sélectionnés  ----")
            for item in data['days']:
                 #Pour chaque jour selectionné, vérifications s'il n'est pas déjà programmé à la même heure sur d'autres planification
                 rqt = "SELECT * FROM schedules WHERE {}=1 AND timeScheduling='{}'"
                 cur.execute(rqt.format(item,time))
                 res = cur.fetchone() 
                 if str(res) == "None": 
                     upd += 1
                     #S'il n'est pas programmé, alors mise à jour de la colonne concernant le jour à 1
                     rqt = "UPDATE schedules SET {}=1 WHERE id={} "
                     cur.execute(rqt.format(item,idScheduling))
                     print(rqt.format(item,idScheduling))
                 logging.info("---- scheduling/PUT : Ajout des jours sélectionnés  ----")
            if upd == 0:
                #Si aucune journée n'a été planifié , alors suppression de la planification
                rqt = "DELETE FROM schedules WHERE id={}"
                cur.execute(rqt.format(idScheduling))
                response ="Planifications non effectuée pour cause de doublons."
                logging.info("---- scheduling/PUT : La planification a été supprimée pour cause de doublons  ----")
            else:
                response ="Planification effectuée."
                logging.info("---- scheduling/PUT : La planification a été supprimée pour cause de doublons  ----")
            
        else:
            response="Erreur lors de la connection à la base de données"
            logging.warning("---- scheduling/PUT : Erreur de connexion à la base de données ----")
    
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
    ''' Récupération de tous les équipements
        Cette fonction permet de récupération tous les équipements
    Args:
    Methods:
    Returns:
       response
    '''
    response=""
    req = "SELECT devices.id,alias,model,host,hardware,mac,led_state,plug,status.status as statut,created_at,updated_at FROM devices left join status on devices.statut = status.id"
    if connDB() is True:
            cur.execute(req.format())
            row_headers=[x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))

            response = json.dumps(json_data,indent=4, sort_keys=True, default=str)
            logging.info("---- devices() : Récupération des informations des équipements ----")
    else:
        response = "Impossible de se connecter à la base de données."
        logging.warning("---- devices() : Impossible de se connecter à la base de données ----")
    return response
  
    
    




app.run(host="0.0.0.0")
