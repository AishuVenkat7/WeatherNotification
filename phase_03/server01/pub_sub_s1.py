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

topics = ['Hourly', 'Daily', 'Weekly'] # server1's responsibility is generate events of these topics

subscriptions = {}

SantaClaraDetails = { 'Hourly': ['SCH1','SCH2'],
'Daily' : ['SCD1','SCD2'],
'Weekly' : ['SCW1','SCW2'],
}

SanFranciscoDetails = { 'Hourly': ['SFH1','SFH2'],
'Daily' : ['SFD1', 'SFD2'],
'Weekly' : ['SFW1','SFW2']
}

DallasDetails = { 'Hourly': ['DAH1','DAH2'],
'Daily' : ['DAD1', 'DAD2'],
'Weekly' : ['DAW1','DAW2']
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


def threadedServerReceiver(connection, jsonData):
    while True:
        serverData = connection.recv(2048).decode()
        m = serverData.split('-')
        if len(m)==3:
            city = m[0]
            topic = m[1]
            event = m[2]
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

    t = Timer(100, getCity)
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
    port = int(os.getenv('SERVER_PORT1'))
    #port = 5029   # Port to listen on (non-privileged ports are > 1023)
    
    # API orders : socket() -> bind() -> listen() -> accept()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating a socket object with TCP protocol. AF_INET is the Internet address family for IPv4.
    
    s.bind((host,port))  # Binding the socket object to a port


    print("Socket is bind to the port :", port)

    s.listen(5)  # Socket is now listening to the port for new connection with 'backlog' parameter value 5. It defines the length of queue for pending connections

    print("Socket is now listening for new connection ...")
    
    # eventGenerator() will be called in a new thread after 10 to 15 seconds
    t = Timer(100, getCity)
    t.start()
    
    # An infinity loop - server will be up for infinity and beyond
    while True:
        
        connection, addr = s.accept()  # Waiting for new connection to be accepted
        print('Connected to :', addr[0], ':', addr[1])
        print("Connection string is",connection)
        
        # Receive data (c-name or s-name) from new connection and determine if it is a client or other server
        # c means client and name is the name of the client
        # s maens server and name is the name of the server
        clientData = connection.recv(2048).decode()
          # convert string to dict
        print("clientdata ",clientData)
        try:
            jsonData = None
            jsonData = json.loads(clientData)
            data = jsonData['subscriberName']
        except ValueError as err:
            data = clientData

        print("data ",data)
        if jsonData is None:
           jsonData = { 'subscriberName': data,
               'city': 'San Francisco',
               'topic': 'Daily'
            }

        if data:
            print("Welcome ",data)
        l = data.split('-')
        if l[0]=='c':
            clientList.append(l[1])
            start_new_thread(threadedClient, (connection, l[1]))
        if l[0]=='s':
            start_new_thread(threadedServerSender, (connection,l[1]))
            start_new_thread(threadedServerReceiver, (connection,jsonData))

    s.close()


if __name__ == '__main__':
    Main() 
