import websockets
import asyncio
import os
import configparser
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
    GPIO.setup(5, GPIO.IN ,pull_up_down=GPIO.PUD_DOWN)
    GP_APP = True
except:
    GP_APP = False

FORMAT = '%(asctime)-15s  %(message)s'
class WebSocketClient():

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("conf.config")
        self.cleint_id = config['DEFAULT']['chat_id']
        self.app_key = config['DEFAULT']['app']
        logging.basicConfig(filename="flat-{0}.log".format(self.cleint_id),level=logging.WARNING,format=FORMAT)

    async def connect(self):
        '''
            Connecting to webSocket server

            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''
        self.connection = await websockets.client.connect("ws://ewtm.ru/ws/chat/{0}/".format(self.cleint_id))
        if self.connection.open:
            print('Connection stablished. Client correcly connected')
            # Send greeting
            await self.sendMessage('Hey server, this is FLAT ID: {0} / FW v 1.0'.format(self.cleint_id))
            return self.connection


    async def sendMessage(self, message):
        '''
            Sending message to webSocket server
        '''
        await self.connection.send(message)

    async def receiveMessage(self, connection):
        '''
            Receiving all server messages and handling them
        '''
        while True:
            try:
                message = json.loads(await connection.recv())
                if message['appid'].replace("\"",'') == self.app_key:
                    if message['message'].replace("\"",'') == 'open':
                        await self.openDoor()
                    elif message['message'].replace("\"",'') == 'update':
                        await self.update()
                    elif message['message'].replace("\"",'') == 'sendlog':
                        await self.sendMessage('LOG HAS BEEN SENT!')
                    elif message['message'].replace("\"",'') == 'ping':
                        await self.sendMessage('PONG FLAT ID: {0}'.format(self.cleint_id))
                    else:
                        pass
                else:
                    print("Wrong APP KEY")
                    logging.error('Wrong APP KEY')
                print('Received message from server: ' + str(message))
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

    async def heartbeat(self, connection):
        '''
        Sending heartbeat to server every 5 seconds
        Ping - pong messages to verify connection is alive
        '''
        while True:
            '''
            if GP_APP:
                if int(GPIO.input(4)) == 1:
                    print("box opened")
                    await self.sendMessage("box opened")
                    await asyncio.sleep(5)
                if int(GPIO.input(5)) == 1:
                    print("door opened")
                    await self.sendMessage("door opened")
                    await asyncio.sleep(5)
            '''
            
            try:
                await connection.ping()
                print("it was ping")
                await asyncio.sleep(5)
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

    async def openDoor(self):
        if GP_APP:
            GPIO.output(2, True)
            time.sleep(5)
            GPIO.output(2, False)
        logging.warning('Door opened...')
        await self.sendMessage('openDoor')

    async def update(self):
        logging.warning('Update...')
        await self.sendMessage('updating software....')
        if GP_APP:
            os.system('sudo rm -r updateme')
            os.system('git clone https://github.com/Woppilif/updateme.git')
            os.system('sudo cp updateme/client.py ./')
            os.system('sudo chmod 777 client.py')
            os.system('sudo cp updateme/update.sh ./')
            os.system('sudo chmod 777 update.sh')
            os.system('sudo reboot')


if __name__ == '__main__':
    # Creating client object
    while True:
        try:
            client = WebSocketClient()
            loop = asyncio.get_event_loop()
            # Start connection and get client connection protocol
            connection = loop.run_until_complete(client.connect())
            # Start listener and heartbeat 
            tasks = [
                asyncio.ensure_future(client.heartbeat(connection)),
                asyncio.ensure_future(client.receiveMessage(connection)),
            ]

            loop.run_until_complete(asyncio.wait(tasks))
        except:
            pass