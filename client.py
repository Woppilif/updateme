#2020
import asyncio
import websockets
import os
import configparser
import requests
import uuid
import hashlib
import json
import time
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(2, GPIO.OUT)
    GPIO.output(2, False)
    GPIO.setup(3, GPIO.OUT)
    GPIO.output(3, False)
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(5, GPIO.IN ,pull_up_down=GPIO.PUD_UP)
    GP_APP = True
except:
    GP_APP = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def loadData():
    config = configparser.ConfigParser()
    config.read(os.path.join(BASE_DIR, 'updateme/conf.config'))
    return config['DEFAULT']['chat_id'], config['DEFAULT']['app']

def getConfig(url):
    if os.path.isfile(os.path.join(BASE_DIR, 'updateme/conf.config')) is False:
        dkey = str(uuid.uuid4())
        response = requests.get("http://{0}/device/{1}".format(url,dkey))
        if response.status_code == 200:
            json_data = json.loads(response.text)
            if "id" in json_data:
                code = hashlib.md5()
                codex = "{0}{1}".format(dkey,json_data['id'])
                code.update(codex.encode())
                config = configparser.ConfigParser()
                config['DEFAULT'] = {'chat_id': json_data['id'],
                                    'app': code.hexdigest(),
                                    'open': dkey}
                with open(os.path.join(BASE_DIR, 'updateme/conf.config'), 'w') as configfile:
                    config.write(configfile)
                return True
            else:
                return getConfig()
        else:
            return getConfig()
                
    else:
        return True

async def connect(url,id):
    try:
        connection = await websockets.client.connect("wss://{0}/ws/chat/{1}/".format(url,id))
        if connection.open:
            print("connecting")
            await connection.send('Hey server, this is DEVICE ID: {0} / FW v 2.0'.format(id))
            return connection
    except:
        print("reconnecting")
        await asyncio.sleep(5)
        return await connect(url,id)
    

async def receiveMessage(connection,app):
    while True:
        greeting = await connection.recv()
        message = json.loads(greeting)
        print(message)
        if "appid" not in message:
            continue
        if message['appid'] != app:
            continue
        await connection.send(command(message['message'])) 

def openDoor():
    if GP_APP:
        GPIO.output(2, True)
        time.sleep(5)
        GPIO.output(2, False)
    print("[COMMAND] open door")
    return "[COMMAND] open door"
    
'''
async def deleteLog(self):
    try:
        os.remove("flat-{0}.log".format(cleint_id))
        status = True
    except:
        status = False  
    logging.warning('log has been deleted') 
    await sendMessage('DELETE LOG FLAT ID: {0}, Response: {1}'.format(cleint_id,status))
'''

def update():
    if GP_APP:
        os.system('sudo rm -r updateme')
        os.system('git clone https://github.com/Woppilif/updateme.git')
        os.system('sudo cp updateme/client.py ./')
        os.system('sudo chmod 777 client.py')
        os.system('sudo cp updateme/update.sh ./')
        os.system('sudo chmod 777 update.sh')
        os.system('sudo reboot')
    return "Updating"

def updatenew():
    if GP_APP:
        os.system('sudo rm -r updateme')
        os.system('git clone https://github.com/Woppilif/updateme.git')
        os.system('sudo cp updateme/client.py ./')
        os.system('sudo chmod 777 client.py')
        #os.system('sudo cp updateme/update.sh ./')
        #os.system('sudo chmod 777 update.sh')
        os.system('sudo service blink restart')
    return "Updating"

def checkping():
    return "Ping-Pong"

def command(command):
    commands = {
        "open":openDoor,
        "update":update,
        "updatenew":updatenew,
        "ping":checkping
    }
    if command not in commands:
        return "Keine"
    function = commands.get(command)
    return function()

async def ping(connection):
    while True:
        await connection.ping()
        await asyncio.sleep(5)

if __name__ == "__main__":
    while True:
        url = "ewtm.ru"
        getConfig(url)
        chat_id, app = loadData()
        loop = asyncio.get_event_loop()
        connection = loop.run_until_complete(connect(url,chat_id))
        tasks = [
            asyncio.ensure_future(ping(connection)),
            asyncio.ensure_future(receiveMessage(connection,app)),
        ]
        loop.run_until_complete(asyncio.wait(tasks))
        
