import sys
import socket
import json
import os
from datetime import datetime

latestTime = 0

def tick(latestTime, requestTime):
        latestTime = max(int(latestTime), int(requestTime))
        latestTime = latestTime + 1
        return latestTime

def Main():

    # localhost # alias of server 02 in docker network
    host = os.getenv('SERVER_HOST2')
    port = int(os.getenv('SERVER_PORT2'))
    subscriberName = str(sys.argv[1])
    counter = 0
    # Getting the current date and time
    dt = datetime.now()
    counter = tick(latestTime, counter)
    print("Timestamp: ",dt, " Lamport timestamp: ", counter)
    subscriptionData = {'subscriberName': subscriberName,
                        'city': 'Santa Clara',
                        'topic': 'Warning',
                        'counter': counter
                        }
    # convert to string
    stringData = json.dumps(subscriptionData)

    print("Subscriber is :", subscriptionData['subscriberName'])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))  # Connect to server

    flag = True

    while True:

        if flag:
            s.send(stringData.encode())
            flag = False

        data = s.recv(2048).decode()
        print("Weather report: ", data)
        # counter = s.recv(2048).decode()
        buf = ''
        try:
            while ' ' not in buf:
                buf += s.recv(2048).decode()
                counter = int(buf)
        except ValueError:
            counter = counter + 1
        print(data)
        dt = datetime.now()
        counter = tick(latestTime,counter)
        print("Message received at: ",dt, " Lamport timestamp: ", counter)


if __name__ == '__main__':
    Main()
