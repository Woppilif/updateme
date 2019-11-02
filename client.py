import RPi.GPIO as GPIO
import os
import asyncio
import websockets
from websockets.exceptions import InvalidStatusCode, ConnectionClosedError
import time
import json
import logging
import configparser

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(2, GPIO.OUT)
GPIO.output(2, False)

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
        appl_key = greeting['appid'].replace("\"",'')
        if appl_key == APP_KEY:
            if message == 'update':
                logging.info('Update...')
                os.system('sh update.sh')
            elif message == 'open':
                
                GPIO.output(2, True)
                time.sleep(5)
                GPIO.output(2, False)
                print("opening...")
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
        
while True:
    try:
        asyncio.get_event_loop().run_until_complete(Run())
    except:
        pass
