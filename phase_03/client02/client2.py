import sys
import socket
import json
import os


def Main():

    # localhost # alias of server 02 in docker network
    host = os.getenv('SERVER_HOST2')
    port = int(os.getenv('SERVER_PORT2'))
    subscriberName = str(sys.argv[1])
    subscriptionData = {'subscriberName': subscriberName,
                        'city': 'Santa Clara',
                        'topic': 'Warning'
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
        print(data)


if __name__ == '__main__':
    Main()
