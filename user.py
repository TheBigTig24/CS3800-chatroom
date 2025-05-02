import socket
import threading
from io import BytesIO
import io
from PIL import Image
import numpy as np
import cv2

name = input("yo name? ")

host = socket.gethostname()
port = 5000

client = socket.socket()
client.connect((host, port))

# receives msg from server
# also sends user if asked
def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            print(msg)
            if msg == 'gimme yo name bru:':
                client.send(name.encode())
            elif msg.startswith('/img'):
                print('Receiving image...')
                image_data: bytes = client.recv(4096)
                data = b'' + image_data
                print('1')
                nparr = np.frombuffer(data, np.byte)
                print('2')
                image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                print('3')
                cv2.imshow('Received Image', image_cv2)
                print('4')
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print(msg)
        except Exception as e:
            print(f"Error receiving message: {e}")
            client.close()
            break
        
def send():
    while True:
        text = input('')
        message = name + ': ' + text
        client.send(message.encode())
        
sendThread = threading.Thread(target=send)
receiveThread = threading.Thread(target=receive)

sendThread.start()
receiveThread.start()