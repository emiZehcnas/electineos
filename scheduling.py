import sys
import json
import asyncio
import mariadb
import datetime
import calendar
import logging
from kasa import SmartPlug
from kasa import SmartDevice
from pprint import pformat as pf
from datetime import datetime
from datetime import date
from pprint import pformat as pf

logging.basicConfig(filename='/home/pi/api/log/'+str(date.today())+'_Electineos_scheduling.log', level=logging.INFO)

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
        logging.info("Connexion à la base de données")
        return True
    except mariadb.Error as e:
        stateConn = "Error: {e}"
        logging.error("Erreur de connexion à la base de données")
        return False
    
async def connSmart(host):
    global dev
    global plug
    try:
       dev = SmartDevice(host)
       await(dev.update())
       
       plug = SmartPlug(host)
       await(plug.update())
       logging.info("Connexion à l'équipement "+host)
       return True
    except:
       logging.error("Erreur de connexion à l'équipement "+host)
       return False



async def getHost(idDevice):
    host=""
    if await(connDB()) is True:
           try:
              rqt = "SELECT host from devices WHERE id='{}'"
              cur.execute(rqt.format(idDevice))
              field_name = [field[0] for field in cur.description]
              res = cur.fetchone()
              value = dict(zip(field_name, res))
              host = value['host']
              logging.info("récupération des informations de l'équipement "+host)
           except:
              host="0000"
    return host
    
    
    
    
              
async def scheduling():
     action=""
     host=""
     plugState=""
     idDevice=0
     host=""
     if await (connDB()) is True:
         try:
             #get current day        
             my_date = date.today()
             #'Wednesday
             print(calendar.day_name[my_date.weekday()])
             dayOfWeek =calendar.day_name[my_date.weekday()]
             currentHour = datetime.now().strftime("%H:%M")
             rqt = "SELECT * FROM schedules WHERE "+dayOfWeek+"=TRUE AND timeScheduling='"+currentHour+"' AND isActive=TRUE"
             #rqt = "SELECT * FROM scheduling WHERE "+dayOfWeek+"=TRUE"
             print(rqt) 
             cur.execute(rqt.format())
             row_headers=[x[0] for x in cur.description]
             print(currentHour) 
             rv = cur.fetchall()
             for result in rv:
                 value = dict(zip(row_headers, result))
                 action = value['actionScheduling']
                 idDevice = value['device']
                 host = await(getHost(idDevice))
                 print(host)
                 print(idDevice)
                 if await(connSmart(host)) is True:
                     if action == 1:
                         if plug.is_off:
                             await(plug.turn_on())
                             plugState="on"
                             logging.info("---- Equipement activé ----")
                     elif action ==0:
                         if plug.is_on:
                             await(plug.turn_off())
                             plugState="off"
                             logging.info("---- Equipement désactivé ----")
                     rqt = "UPDATE devices SET alias='{}', model='{}', hardware='{}', mac='{}', led_state='{}', plug = '{}', statut='{}',updated_at='{}' WHERE id='{}' "
                     cur.execute(rqt.format(dev.alias,dev.model,dev.hw_info["hw_ver"],dev.mac,plug.led,plugState,1,datetime.now(),idDevice))
         except:
             print("Une erreur est survenue")
             logging.error("---- Une erreur est survenue ----")
     else:
         logging.warning("---- Erreur lors de la connexion à la base de données ----")
         #print("ko")                   
      

asyncio.run(scheduling())                        