# Pub-Sub-Distributed-System-Using-Docker

Publish/Subscribe (or pub/sub for short) is a popular **indirect** communication system. `Pub/sub` systems disseminates events to multiple recipients (called subscribers) through an intermediary. Examples of successful pub/sub include `Twitter` and `Bloomberg terminal`-like financial systems. In this project, we will emulate a pub/sub system using `Docker` which is a computer program that performs operating-system-level virtualization, also known as "containerization".

# How to run phase-02 
`(Distributed Publisher/Subscriber System)`

First go the `phase_02` directory. Then run the below commands:

```
docker build -t pubsub-image:v1 . #create new image for pubsub application
docker run -d -p 80:80 --name pubsub_central pubsub-image:v1 #running image in a new container
```
Now go to url `localhost:80` to see the output of the app from docker.

<img width="817" alt="publisher" src="https://github.com/user-attachments/assets/06eeaa0f-6082-471f-92b8-d4a8a4962dc9">
<img width="849" alt="subscriber" src="https://github.com/user-attachments/assets/ded8a18b-ac0b-43c6-9751-3b2da1e1f447">
<img width="865" alt="publishing" src="https://github.com/user-attachments/assets/81c0d05a-e1be-4ecf-a85d-5ffc843fbb3f">
<img width="865" alt="getting_subscription_msg" src="https://github.com/user-attachments/assets/eb425ccc-33e2-4683-9654-59f59e9ec60e">
<img width="868" alt="unsubscribing" src="https://github.com/user-attachments/assets/9d2cd9bb-e7dd-4eee-a847-84c16a99fa14">

# How to run phase-03 
`(Distributed Publisher/Subscriber System with distributed servers)`

First go the `phase_03` directory. Then run the below commands:

```
docker-compose up

```

If you want to stop the servers, then press `Ctrl+C`

<img width="949" alt="phase3" src="https://github.com/user-attachments/assets/e5042564-ccc7-4867-a474-f58df04b2918">



