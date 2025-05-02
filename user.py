import socket
import threading
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
            if msg == 'gimme yo name bru:':
                client.send(name.encode())
            elif msg.startswith('/img'):  
                # receive the image
                theLengthTypeShi = msg.split(' ')[1]
                image_data: bytes = client.recv(8192)
                
                if len(image_data) == int(theLengthTypeShi):
                    data = b'' + image_data
                    nparr = np.frombuffer(data, np.byte)
                    image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    cv2.imshow('Received Image', image_cv2)
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