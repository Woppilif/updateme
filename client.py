import websockets
from websockets.exceptions import InvalidStatusCode, ConnectionClosedError
import configparser
import os
import asyncio
import time
import json
import logging
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(2, GPIO.OUT)
    GPIO.output(2, False)
    GP_APP = True
except:
    GP_APP = False
FORMAT = '%(asctime)-15s  %(message)s'

class Flat():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("conf.config")
        self.cleint_id = config['DEFAULT']['chat_id']
        self.app_key = config['DEFAULT']['app']
        self.message = None
        self.ws_object = websockets.connect("ws://www.ewtm.ru/ws/chat/{0}/".format(self.cleint_id))
        logging.basicConfig(filename="flat-{0}.log".format(self.cleint_id),level=logging.DEBUG,format=FORMAT)
    
    async def readMessage(self):
        self.message = json.loads(self.message)
        if self.message['appid'].replace("\"",'') == self.app_key:
            if self.message['message'].replace("\"",'') == 'open':
                self.openDoor()
                await self.sendMessage('openDoor')
            elif self.message['message'].replace("\"",'') == 'update':
                self.update()
            else:
                pass
        else:
            logging.warning('Wrong APP KEY')
        self.message = None
        

    async def getMessage(self):
        async with self.ws_object as websocket:
            print("Listening....")
            self.message  = await websocket.recv()

    async def sendMessage(self,message):
        async with self.ws_object as websocket:
            print("Message has been sent!")
            await websocket.send(message)


    async def Run(self):
        while True:
            try:
                await self.getMessage()
            except ConnectionClosedError:
                print("Disconnected! Trying to reconnect!")
                time.sleep(5)
            except InvalidStatusCode:
                print("InvalidStatusCode! Trying to connect to server.....!")
                time.sleep(5)
            except ConnectionRefusedError:
                print("ConnectionRefusedError! Trying to connect to server.....!")
                time.sleep(5)
            finally:
                 if self.message is not None:
                    await self.readMessage()
                    

    def update(self):
        logging.info('Update...')
        os.system('sh update.sh')

    def openDoor(self):
        if GP_APP:
            GPIO.output(2, True)
            time.sleep(5)
            GPIO.output(2, False)
        
        logging.info('Door opened...')
        print("opened!")

    def doorOpened(self):
        pass

    def doorClosed(self):
        pass

while True:
    try:
        asyncio.get_event_loop().run_until_complete(Flat().Run())
    except:
        pass
