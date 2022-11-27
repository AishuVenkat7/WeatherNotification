import socket
import sys
import random
import os
import json

from _thread import *
from threading import Timer


# Topic based pub-sub -- Multithreading and Socket is needed for implementation

# Global variables

clientList = []

locations = ['Santa Clara','San Francisco','Dallas']

all_topics = ['Hourly', 'Daily', 'Weekly', 'Warning']

topics = ['Warning'] # server2's responsibility is generate events of these topics

subscriptions = {}

SantaClaraDetails = { 'Warning': ['SC_W1','SC_W2']
}

SanFranciscoDetails = { 'Warning': ['SF_W1','SF_W2']
}

DallasDetails = { 'Warning': ['DA_W1','DA_W2']
}
mapping = {
  "Santa Clara" : SantaClaraDetails,
  "San Francisco" : SanFranciscoDetails,
  "Dallas" : DallasDetails
}


# { subscriberName : [msg1, msg2,, ] , ... }
generatedEvents = dict()

flags = dict()

# Handle any client's connection

def threadedClient(connection, name):
    while True:
        flags[name] = 0
        subscribe(name) # Generate subscription for the connected subscriber
        subscriptionInfo = 'Your subscriptions are : ' + str(subscriptions[name])
        connection.send(subscriptionInfo.encode())
        
        while True:
            if flags[name]==1:
                notify(connection,name)

    connection.close()



# Handle other server's connection

# Send to other servers
def threadedServerSender(connection, name):
    while True:
        flags[name] = 0
        subscriptions[name] = topics  # Other server's  are subscribed to the all topics of this server
        subscriptionInfo = 'Your subscriptions are : ' + str(subscriptions[name])
        connection.send(subscriptionInfo.encode())
        
        while True:
            if flags[name]==1:
                notify(connection,name)
    connection.close()


# Receive from other servers
def threadedServerReceiver(connection, data):
    while True:
        serverData = connection.recv(2048).decode()
        m = serverData.split('-')
        if len(m)==3:
            city = m[0]
            topic = m[1]
            event = m[2]
            publish(topic,event,city,0)
    connection.close()


# Send to master server
def threadedMasterSender(ss):
    while True:
        flags['master'] = 0
        subscriptions['master'] = topics  # Other server's  are subscribed to the all topics of this server
        subscriptionInfo = 'Your subscriptions are : ' + str(subscriptions['master'])
        ss.send(subscriptionInfo.encode())
        
        while True:
            if flags['master']==1:
                notify(ss,'master')
    ss.close()

# Receive from master server
def threadedMasterReceiver(ss):
    while True:
        serverData = ss.recv(2048).decode()
        if serverData:
            print("Received from MASTER :",serverData)
            p = serverData.split('-')
            if len(p)==3:
                city = p[0]
                topic = p[1]
                event = p[2]
                publish(topic,event,city,0)
    connection.close()



## SUBSCRIBE()


def subscribe(name):
    subscriptions[name] = randomSubscriptionGenerator()


def randomSubscriptionGenerator():
    subscribedTopicsList = random.sample(all_topics,random.choice(list(range(1,len(all_topics)+1))))
    return subscribedTopicsList



def getCity():
    city = random.choice(locations)
    print("city chosen: " + city)
    eventGenerator(city)

## PUBLISH() and ADVERTIZE()

def eventGenerator(city):

    for i in locations:
        if city == i:
            topic = random.choice(topics)
            map = mapping[i]
            msgList = map[topic]
            print("This is msg: ", msgList)
            event = msgList[random.choice(list(range(1,len(msgList))))]
 
    publish(topic,event,city,1) # call publish() for publishing the new event


def publish(topic,event,city,indicator):
    
    event = city + '-' + topic + '-' + event  # Concatenate topic and event
    print(event)  # print the event in server console

    # publishing generated events to interested subscriber (subscribers + other servers)
    if indicator == 1:
        for name, topics in subscriptions.items() :
            if topic in topics:
                if name in generatedEvents.keys():
                    generatedEvents[name].append(event)
                else:
                    generatedEvents.setdefault(name, []).append(event)
                flags[name] = 1

    # publishing received events to interested subscriber (only subscribers)
    else:
        for name, topics in subscriptions.items() :
            if name in clientList: # only for clients
                if topic in topics:
                    if name in generatedEvents.keys():
                        generatedEvents[name].append(event)
                    else:
                        generatedEvents.setdefault(name, []).append(event)
                    flags[name] = 1

    t = Timer(150, getCity)
    t.start()


def notify(connection,name):
    if name in generatedEvents.keys():
        for msg in generatedEvents[name]:
            msg = msg  # + str("\n")
            connection.send(msg.encode())
        del generatedEvents[name]
        flags[name] = 0



def Main():
    
    host = ""     # Server will accept connections on all available IPv4 interfaces
    port = int(os.getenv('SERVER_PORT2'))
    #port = 5030   # Port to listen on (non-privileged ports are > 1023)
    
    # API orders : socket() -> bind() -> listen() -> accept()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating a socket object with TCP protocol. AF_INET is the Internet address family for IPv4.
    
    s.bind((host,port))  # Binding the socket object to a port
    
    
    print("Socket is bind to the port :", port)
    
    s.listen(5)  # Socket is now listening to the port for new connection with 'backlog' parameter value 5. It defines the length of queue for pending connections
    
    print("Socket is now listening for new connection ...")
    
    
    # eventGenerator() will be called in a new thread after 10 to 15 seconds
    t = Timer(150, getCity)
    t.start()


    # connecting with master server

    master_host = os.getenv('SERVER_HOST1')
    master_port = int(os.getenv('SERVER_PORT1'))
    #master_host = 'server001' # localhost  # alias of server01 in docker network
    #master_port =  5029
   
    serverName = str(sys.argv[1])
    
    ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ss.connect((master_host,master_port))
    ss.send(serverName.encode())
    
    start_new_thread(threadedMasterReceiver, (ss,))
    start_new_thread(threadedMasterSender, (ss,))
    
    
    # An infinity loop - server will be up for infinity and beyond
    while True:
        
        connection, addr = s.accept()  # Waiting for new connection to be accepted
        print('Connected to :', addr[0], ':', addr[1])
        print("Connection string is",connection)
        
        #data = connection.recv(2048).decode()
        #if data:
            #print("Welcome ",data)
        #l = data.split('-')
        clientData = connection.recv(2048).decode()
          # convert string to dict
        data = json.loads(clientData)

        if data:
            print("Welcome ",data['subscriberName'])
        
        l = data['subscriberName'].split('-')
        
        if l[0]=='c':
            clientList.append(l[1])
            start_new_thread(threadedClient, (connection,l[1]))
        if l[0]=='s':
            start_new_thread(threadedServerSender, (connection,l[1]))
            start_new_thread(threadedServerReceiver, (connection,data))

    s.close()


if __name__ == '__main__':
    Main()

