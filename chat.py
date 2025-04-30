import socket
import threading

host = socket.gethostname()
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# list of clients
clients = []

# user names
# parallel array to clients
names = []

# stores users time of most recent message sent
lastActivity = []

# send msg to all clients
# assume that the msg is already encoded
def flood(message, excludedClient = None):
    for client in clients:
        if excludedClient == None or excludedClient.getpeername()[1] != client.getpeername()[1]:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message to {client}: {e}")
                
# handle incoming msgs from each client
def manageClient(client):
    while True:
        try:
            message = client.recv(1024)
            messageDecode = message.decode()
            msg = messageDecode.split(' ', 3)
            if msg[1] == '/r':
                # private message
                if len(msg) == 4:
                    recipient = msg[2]
                    privateMsg = msg[3]
                    if recipient in names:
                        index = names.index(recipient)
                        clients[index].send((f"{names[clients.index(client)]} is hitting u up privately: {privateMsg}").encode())
                    else:
                        client.send(f"User {recipient} not found.".encode())
            else:
                # send msg to all other clients
                flood(message)
            # flood(message)
            
        except Exception as e:
            # error , rm client
            removeClient(client)
            
def removeClient(client):
    index = clients.index(client)
    clients.remove(client)
    name = names[index]
    names.remove(name)
    client.close()
    
    # tell other clients who has left
    leavingMsg = 'ikiag, ' + name + ' skedaddled, ts so kevin'
    flood(leavingMsg.encode())
    
# ts loop is for accepting multiple client connections
while True:
    client, addr = server.accept()
    
    # prompts user for name
    client.send('gimme yo name bru:'.encode())
    
    name = client.recv(1024).decode()
    clients.append(client)
    names.append(name)
    
    # notify all users when a new person joins
    joinMsg = name + ' has joined the kool kidz klub, ts so owen frfr'
    
    client.send((name + ', 微信欢迎你来到聊天室！Use "/r <username> <msg>" to send a dm').encode())
    flood(joinMsg.encode(), client)
    
    print('got connection from ', client.getpeername())
    
    # create new thread for each client
    thread = threading.Thread(target = manageClient, args = (client,))
    thread.start()