import socket
import sys
import random
import os
import json
from datetime import datetime

from _thread import *
from threading import Timer


# Topic based pub-sub -- Multithreading and Socket is needed for implementation

# Global variables

clientList = []

locations = ['Santa Clara', 'San Francisco', 'Dallas']

all_topics = ['Hourly', 'Daily', 'Weekly', 'Warning']

# server1's responsibility is generate events of these topics
topics = ['Hourly', 'Daily', 'Weekly']

subscriptions = {}

SantaClaraDetails = {'Hourly': ['Partly Cloudy, High/Low temperatures today: 62°/39°, Humidity: 58%, Wind speed: NW 10mph, UV Index: 2/10, rain amount: 1%',
                                'Clear, High/Low temperatures today: 60°/37°, Humidity: 48%, Wind speed: SSE 6mph, UV Index: 1/10, rain amount: 0%'],
                     'Daily': ['Heavy Rain, High/Low temperatures today: 45°/12°, Humidity: 80%, Wind speed: S 16mph, UV Index: 1/10, rain amount: 98%',
                               'Sunny, High/Low temperatures today: 62°/46°, Humidity: 45%, Wind speed: SW 8mph, UV Index: 2/10, rain amount: 0%'],
                     'Weekly': ['Showers, High/Low temperatures today: 57°/34°, Humidity: 69%, Wind speed: NNW 11mph, UV Index: 1/10, rain amount: 47%',
                                'Mostly Sunny, High/Low temperatures today: 62°/36°, Humidity: 52%, Wind speed: N 12mph, UV Index: 2/10, rain amount: 1%'],
                     }

SanFranciscoDetails = {'Hourly': ['Rain, High/Low temperatures today: 51°/26°, Humidity: 61%, Wind speed: NNW 14mph, UV Index: 1/10, rain amount: 29%',
                                  'Mostly Sunny, High/Low temperatures today: 54°/37°, Humidity: 43%, Wind speed: SE 6mph, UV Index: 2/10, rain amount: 0%'],
                       'Daily': ['Cloudy, High/Low temperatures today: 55°/38°, Humidity: 56%, Wind speed: S 13mph, UV Index: 1/10, rain amount: 1%',
                                 'Sunny, High/Low temperatures today: 62°/46°, Humidity: 42%, Wind speed: SW 8mph, UV Index: 2/10, rain amount: 0%'],
                       'Weekly': ['Showers, High/Low temperatures today: 57°/29°, Humidity: 69%, Wind speed: NNW 11mph, UV Index: 1/10, rain amount: 34%',
                                  'Sunny, High/Low temperatures today: 62°/36°, Humidity: 52%, Wind speed: N 12mph, UV Index: 2/10, rain amount: 0%'],
                       }

DallasDetails = {'Hourly': ['Sunny, High/Low temperatures today: 67°/39°, Humidity: 41%, Wind speed: NW 6mph, UV Index: 2/10, rain amount: 0%',
                            'Clear, High/Low temperatures today: 60°/37°, Humidity: 48%, Wind speed: SSE 7mph, UV Index: 1/10, rain amount: 0%'],
                 'Daily': ['Heavy Rain, High/Low temperatures today: 39°/14°, Humidity: 90%, Wind speed: S 16mph, UV Index: 1/10, rain amount: 98%',
                           'Snow, High/Low temperatures today: 29°/22°, Humidity: 92%, Wind speed: SW 18mph, UV Index: 1/10, rain amount: 0%'],
                 'Weekly': ['Showers, High/Low temperatures today: 50°/33°, Humidity: 69%, Wind speed: NNW 11mph, UV Index: 1/10, rain amount: 47%',
                            'Mostly Sunny, High/Low temperatures today: 62°/36°, Humidity: 52%, Wind speed: N 7mph, UV Index: 2/10, rain amount: 1%'],
                 }

# mapping city with topics of each city

mapping = {
    "Santa Clara": SantaClaraDetails,
    "San Francisco": SanFranciscoDetails,
    "Dallas": DallasDetails
}

counter = 0
latestTime = 0

def tick(latestTime, requestTime):
        latestTime = max(int(latestTime), int(requestTime))
        latestTime = latestTime + 1
        return latestTime


# { subscriberName : [msg1, msg2,, ] , ... }
generatedEvents = dict()

flags = dict()

# Handle any client's connection


def threadedClient(connection, name, counter):

    
    while True:
        flags[name] = 0
        subscribe(name)  # Generate subscription for the connected subscriber
        subscriptionInfo = 'Your subscriptions are: ' + \
            str(subscriptions[name])
        connection.send(subscriptionInfo.encode())
        val = str(counter) + ' '
        connection.send(val.encode())  #sending lamport timestamp

        while True:
            if flags[name] == 1:
                notify(connection, name, val)
    connection.close()


# Handle other server's connection

def threadedServerSender(connection, name, counter):
    while True:
        flags[name] = 0
        # Other server's  are subscribed to the all topics of this server
        subscriptions[name] = topics
        subscriptionInfo = 'Your subscriptions are: ' + \
            str(subscriptions[name])
        connection.send(subscriptionInfo.encode())
        val = str(counter) + ' '
        connection.send(val.encode())  #sending lamport timestamp
        while True:
            if flags[name] == 1:
                notify(connection, name, val)
    connection.close()


def threadedServerReceiver(connection, jsonData):
    while True:
        serverData = connection.recv(2048).decode()
        buf = ''
        #converting the timestamp to int
        try:
            while ' ' not in buf:
                buf += connection.recv(2048).decode()
                counter = int(buf)
        except ValueError:
            counter = counter + 1
        # Getting the current date and time
        dt = datetime.now()
        counter_flag = tick(latestTime, counter)
        print("Timestamp: ",dt, " Lamport timestamp: ", counter_flag)

        m = serverData.split('-')
        if len(m) == 3:
            city = m[0]
            topic = m[1]
            event = m[2]
            publish(topic, event, city, 0)
    connection.close()


# SUBSCRIBE()

def subscribe(name):
    subscriptions[name] = randomSubscriptionGenerator()


def randomSubscriptionGenerator():
    subscribedTopicsList = random.sample(
        all_topics, random.choice(list(range(1, len(all_topics)+1))))
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
            print("Message: ", msgList)
            event = msgList[random.choice(list(range(1, len(msgList))))]

    # call publish() for publishing the new event
    publish(topic, event, city, 1)


def publish(topic, event, city, indicator):

    # Concatenate city and it topic and event
    event = city + '-' + topic + '-' + event
    print(event)  # print the event in server console

    # publishing generated events to interested subscriber (subscribers + other servers)
    if indicator == 1:
        for name, topics in subscriptions.items():
            if topic in topics:
                if name in generatedEvents.keys():
                    generatedEvents[name].append(event)
                else:
                    generatedEvents.setdefault(name, []).append(event)
                flags[name] = 1

    # publishing received events to interested subscriber (only subscribers)
    else:
        for name, topics in subscriptions.items():
            if name in clientList:  # only for clients
                if topic in topics:
                    if name in generatedEvents.keys():
                        generatedEvents[name].append(event)
                    else:
                        generatedEvents.setdefault(name, []).append(event)
                    flags[name] = 1

    t = Timer(30, getCity)
    t.start()


def notify(connection, name, val):
    if name in generatedEvents.keys():
        for msg in generatedEvents[name]:
            msg = msg  # + str("\n")
            connection.send(msg.encode())  #sending the weather msg
            connection.send(val.encode())  #sending lamport timestamp
        del generatedEvents[name]
        flags[name] = 0


def Main():

    host = ""     # Server will accept connections on all available IPv4 interfaces
    port = int(os.getenv('SERVER_PORT1'))
    # port = 5029   # Port to listen on (non-privileged ports are > 1023)

    # API orders : socket() -> bind() -> listen() -> accept()

    # Creating a socket object with TCP protocol. AF_INET is the Internet address family for IPv4.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((host, port))  # Binding the socket object to a port

    print("Socket is bind to the port: ", port)

    s.listen(5)  # Socket is now listening to the port for new connection with 'backlog' parameter value 5. It defines the length of queue for pending connections

    print("Socket is now listening for new connection ...")

    # getCity() will be called in a new thread after 100 seconds
    t = Timer(30, getCity)
    t.start()

    # An infinity loop - server will be up for infinity and beyond
    while True:

        connection, addr = s.accept()  # Waiting for new connection to be accepted
        print('Connected to: ', addr[0], ':', addr[1])
        print("Connection string is: ", connection)

        # Receive data (c-name or s-name) from new connection and determine if it is a client or other server
        # c means client and name is the name of the client
        # s means server and name is the name of the server
        clientData = connection.recv(2048).decode()

        # convert string to dict
        print("Received data: ", clientData)
        try:
            jsonData = None
            jsonData = json.loads(clientData)
            data = jsonData['subscriberName']
            counter = jsonData['counter']
        except ValueError as err:
            data = clientData

        print("Entity name: ", data)

        # Getting the current date and time
        dt = datetime.now()
        counter_flag = tick(latestTime, counter)
        print("Timestamp now: ",dt, " Lamport timestamp now: ", counter_flag)

        if data:
            print("Welcome ", data)
        l = data.split('-')
        if l[0] == 'c':
            clientList.append(l[1])
            start_new_thread(threadedClient, (connection, l[1], counter))
        if l[0] == 's':
            start_new_thread(threadedServerSender, (connection, l[1], counter))
            start_new_thread(threadedServerReceiver, (connection, jsonData))

    s.close()


if __name__ == '__main__':
    Main()
