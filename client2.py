'''
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Lock.RELAY_CONTROL_PIN, GPIO.OUT)
GPIO.setup(Lock.RELAY_PROTECTION_PIN, GPIO.OUT)
GPIO.output(Lock.RELAY_CONTROL_PIN, False)
GPIO.output(Lock.RELAY_PROTECTION_PIN, False)
'''

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
    async with websockets.connect("ws://127.0.0.1:8000/ws/chat/{0}/".format(config['DEFAULT']['chat_id'])) as websocket:
        print("Listening....")
        greeting = await websocket.recv()
        greeting = greeting.replace("'", "\"")
        greeting = json.loads(greeting)
        message = greeting['message'].replace("\"",'')
        if message == 'update':
            logging.info('Update...')
            os.system('git clone https://github.com/Woppilif/updateme.git .')
        elif message == APP_KEY:
            '''
            GPIO.output(2, True)
            time.sleep(5)
            GPIO.output(2, False)
            '''

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