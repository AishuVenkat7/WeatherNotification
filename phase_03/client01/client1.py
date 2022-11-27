import sys
import socket
import json
import os

def Main():

    host = os.getenv('SERVER_HOST1')
    port = int(os.getenv('SERVER_PORT1'))
    subscriberName = str(sys.argv[1])
    subscriptionData  = { 'subscriberName': subscriberName,
               'city': 'Santa Clara',
               'topic': 'Daily'
            }
    ## convert to string
    stringData = json.dumps(subscriptionData)
    
    #host = 'server001' # localhost  # alias of server 01 in docker network
    #port =  5029
    #subscriberName = str(sys.argv[1])

    print("Subscriber is :",subscriptionData['subscriberName'])

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))  # Connect to server
    
    flag = True
    
    while True:
       
        if flag:
            s.send(stringData.encode())
            flag = False
        
        data = s.recv(2048).decode()
        print(data)


if __name__ == '__main__':
    Main() 
