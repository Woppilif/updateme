from lock import Lock
import asyncio
#HELLO
import RPi.GPIO as GPIO
# lock = Lock()
# asyncio.run(lock.open())

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Lock.RELAY_CONTROL_PIN, GPIO.OUT)
GPIO.setup(Lock.RELAY_PROTECTION_PIN, GPIO.OUT)
GPIO.output(Lock.RELAY_CONTROL_PIN, False)
GPIO.output(Lock.RELAY_PROTECTION_PIN, False)
from lock import Lock
import asyncio

import RPi.GPIO as GPIO
# lock = Lock()
# asyncio.run(lock.open())

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Lock.RELAY_CONTROL_PIN, GPIO.OUT)
GPIO.setup(Lock.RELAY_PROTECTION_PIN, GPIO.OUT)
GPIO.output(Lock.RELAY_CONTROL_PIN, False)
GPIO.output(Lock.RELAY_PROTECTION_PIN, False)

import os
import asyncio
import websockets
from websockets.exceptions import InvalidStatusCode, ConnectionClosedError
import time
import json
import logging
import configparser
config = configparser.ConfigParser()
config.read("conf.config")

FORMAT = '%(asctime)-15s  %(message)s'
logging.basicConfig(filename='example.log',level=logging.DEBUG,format=FORMAT)

APP_KEY = config['DEFAULT']['app']

async def hello():
    async with websockets.connect("ws://www.ewtm.ru/ws/chat/{0}/".format(config['DEFAULT']['chat_id'])) as websocket:
        print("Listening....")
        greeting = await websocket.recv()
        greeting = greeting.replace("'", "\"")
        greeting = json.loads(greeting)
        message = greeting['message'].replace("\"",'')
        if message == 'update':
            logging.info('Update...')
            os.system('sh update.sh')
        elif message == APP_KEY:
            
            GPIO.output(2, True)
            time.sleep(5)
            GPIO.output(2, False)
            

            logging.info('Opening door')
        else:
            logging.warning('Wrong APP KEY')
        

 
async def Run():
    while True:
        try:
            await hello()
        except ConnectionClosedError:
            print("Disconnected! Trying to reconnect!")
            time.sleep(5)
        except InvalidStatusCode:
            print("InvalidStatusCode! Trying to connect to server.....!")
            time.sleep(5)
        except ConnectionRefusedError:
            print("ConnectionRefusedError! Trying to connect to server.....!")
            time.sleep(5)
        
asyncio.get_event_loop().run_until_complete(Run())