import socket
import threading

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
            else:
                print(msg)
        except:
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