import socket
import threading
import datetime
import time

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
# stores maps with keys: user, time, message
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
            
            # check for private message
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
                        # update last activity
                        activity = {'user': names[clients.index(client)], 'time': datetime.datetime.now(), 'message': privateMsg}
                        lastActivity.append(activity)
                    else:
                        client.send(f"User {recipient} not found.".encode())
            elif msg[0] == 'admin:' and msg[1] == '/kick':
                # kick a user
                thePersonToKick = msg[2]
                if thePersonToKick in names:
                    index = names.index(thePersonToKick)
                    clients[index].send('you have been kicked by admin'.encode())
                    removeClient(clients[index])
                    # update last activity
                    activity = {'user': names[clients.index(client)], 'time': datetime.datetime.now(), 'message': f'kicked {thePersonToKick}'}
                    lastActivity.append(activity)
                else:
                    client.send(f"User {thePersonToKick} not found.".encode())
            else:
                # send msg to all other clients
                flood(message)
                # update last activity
                combinedMsg = ''
                for index in range(1, len(msg)):
                    combinedMsg += msg[index]
                activity = {'user': names[clients.index(client)], 'time': datetime.datetime.now(), 'message': combinedMsg}
                lastActivity.append(activity)
                
            
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
    
    
# start the inactivity-checker-inator
def i_call_this_the_inactivity_checker_inator():
    while True:
        # check for inactivity every 5 seconds
        time.sleep(5)
        
        # this if statement is to prevent kicking users on join since they have no previous messages
        if len(lastActivity) != 0:
            # check people that have sent a message before
            thesePeopleHaveSpoken = [activity['user'] for activity in lastActivity]
            
            # check if they have been active in the last 30 seconds
            afkers = names.copy()
            currentTime = datetime.datetime.now()
            for activity in lastActivity:
                currName = activity['user']
                lastTime = activity['time']
                timeDiff = currentTime - lastTime
                if timeDiff.total_seconds() < 30:
                    # remove users that have been active in the last 30 seconds and have typed at least one message
                    if (currName in afkers) and (currName in thesePeopleHaveSpoken):
                        afkers.remove(currName)
                    
            # remove all users that are inactive for more than 30 seconds
            afkers = list(set(afkers))
            for stupidMoron in afkers:
                try:
                    index = names.index(stupidMoron)
                    clients[index].send('you have been away from the k for too long, ur gone buddy'.encode())
                    removeClient(clients[index])
                    lastActivity[:] = [activity for activity in lastActivity if activity['user'] != stupidMoron]
                except Exception as e:
                    print(f"Error removing client {stupidMoron}: {e}")

# start the inactivity checker thread
inactivity_thread = threading.Thread(target = i_call_this_the_inactivity_checker_inator)
inactivity_thread.daemon = True
inactivity_thread.start()            
            
# ts loop is for accepting multiple client connections
while True:
    client, addr = server.accept()
    
    # prompts user for name
    client.send('gimme yo name bru:'.encode())
    
    name = client.recv(1024).decode()
    
    # check if admin
    if name == 'admin':        
        askPassword = 'whats the password? '
        client.send(askPassword.encode())
        pwAttempt = client.recv(1024).decode()
        tries = 0
        while tries < 3 and pwAttempt.split(' ', 1)[1] != 'ongurt':
            tryAgainMessage = 'WRONGGGG!!!!! ' + askPassword
            client.send(tryAgainMessage.encode())
            pwAttempt = client.recv(1024).decode()
            tries += 1
            
        if pwAttempt.split(' ', 1)[1] == 'ongurt':
            clients.append(client)
            names.append(name)
            client.send('welcome to the light side'.encode())
            flood('admin has joined'.encode(), client)
            print('got connection from ', client.getpeername())
            
            thread = threading.Thread(target = manageClient, args = (client,))
            thread.start()
        if tries >= 3:
            client.send('bro tryna hack'.encode())
            client.close()
    else:
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