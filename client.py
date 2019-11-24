import asyncio
import websockets
from websockets.exceptions import InvalidStatusCode, ConnectionClosedError, InvalidMessage
import os
import configparser
import time
import json
import logging
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

FORMAT = '%(asctime)-15s  %(message)s'
class Flat():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("conf.config")
        self.cleint_id = config['DEFAULT']['chat_id']
        self.app_key = config['DEFAULT']['app']
        self.message = None
        self.ws_object = websockets.connect("ws://ewtm.ru/ws/chat/{0}/".format(self.cleint_id))
        logging.basicConfig(filename="flat-{0}.log".format(self.cleint_id),level=logging.WARNING,format=FORMAT)
    
    def update(self):
        logging.warning('Update...')
        if GP_APP:
            os.system('sudo rm -r updateme')
            os.system('git clone https://github.com/Woppilif/updateme.git')
            os.system('sudo cp updateme/client.py ./')
            os.system('sudo chmod 777 client.py')
            os.system('sudo cp updateme/update.sh ./')
            os.system('sudo chmod 777 update.sh')
            os.system('sudo reboot')
        

    def openDoor(self):
        if GP_APP:
            GPIO.output(2, True)
            time.sleep(5)
            GPIO.output(2, False)
        
        logging.warning('Door opened...')
        print("opened!")

    async def sendLog(self):
        fil = []
        async with open("flat-{0}.log".format(self.cleint_id), 'r') as f:
            await self.sendMessage(str(f))
        
        

    async def sendMessage(self,message):
        async with self.ws_object as websocket:
            print("Message has been sent!")
            await websocket.send(message)

    async def readMessage(self):
        self.message = json.loads(self.message)
        if self.message['appid'].replace("\"",'') == self.app_key:
            if self.message['message'].replace("\"",'') == 'open':
                self.openDoor()
                await self.sendMessage('openDoor')
            elif self.message['message'].replace("\"",'') == 'update':
                self.update()
                await self.sendMessage('updating software....')
            elif self.message['message'].replace("\"",'') == 'sendlog':
                #await self.sendLog()
                await self.sendMessage('LOG HAS BEEN SENT!')
            else:
                pass
        else:
            logging.error('Wrong APP KEY')
        self.message = None

    async def getMessage(self):
        async with self.ws_object as websocket:
            await asyncio.sleep(0)
            print("Listening...")
            while True:
                self.message = await websocket.recv()
                await self.readMessage()

    async def answer(self):
        print("File destructor is here")
        while True:
            if GP_APP:
                if int(GPIO.input(4)) == 0:
                    print("box opened")
                    await asyncio.sleep(10)
                    await self.sendMessage("box opened")
                if int(GPIO.input(5)) == 1:
                    print("door opened")
                    await asyncio.sleep(5)
                    await self.sendMessage("door opened")
            await asyncio.sleep(0)
           

    async def Run(self):
        while True:
            try:
                await self.getMessage()
            except ConnectionClosedError:
                print("Disconnected! Trying to reconnect!")
                logging.error('Disconnected! Trying to reconnect!')
                await asyncio.sleep(5)
            except InvalidStatusCode:
                print("InvalidStatusCode! Trying to connect to server.....!")
                logging.error('InvalidStatusCode! Trying to connect to server.....!')
                await asyncio.sleep(5)
            except ConnectionRefusedError:
                print("ConnectionRefusedError! Trying to connect to server.....!")
                logging.error('ConnectionRefusedError! Trying to connect to server.....!')
                await asyncio.sleep(5)
            except InvalidMessage:
                print("InvalidMessage! Trying to connect to server.....!")
                logging.error('InvalidMessage! Trying to connect to server.....!')
                await asyncio.sleep(5)


while True:
    
    flat = Flat()
    loop = asyncio.get_event_loop()
    tasks = []
    tasks.append(loop.create_task(flat.Run()))
    tasks.append(loop.create_task(flat.answer()))
    x = asyncio.gather(*tasks)
    loop.run_until_complete(x)
    
  