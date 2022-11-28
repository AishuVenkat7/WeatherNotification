# Pub-Sub-Distributed-System-Using-Docker

Publish/Subscribe (or pub/sub for short) is a popular **indirect** communication system. `Pub/sub` systems disseminates events to multiple recipients (called subscribers) through an intermediary. Examples of successful pub/sub include `Twitter` and `Bloomberg terminal`-like financial systems. In this project, we will emulate a pub/sub system using `Docker` which is a computer program that performs operating-system-level virtualization, also known as "containerization".

# How to run phase-02 
`(Distributed Publisher/Subscriber System with a Central Server)`

First go the `phase_02` directory. Then run the below commands:

```
docker build -t pubsub-image:v1 . #create new image for pubsub application
docker run -d -p 80:80 --name pubsub_central pubsub-image:v1 #running image in a new container
```
Now go to url `localhost:80` to see the output of the app from docker.

There are screenshots available in the repo under the Screenshots folder.

# How to run phase-03 
`(Distributed Publisher/Subscriber System with distributed servers)`

First go the `phase_03` directory. Then run the below commands:

```
docker-compose up

```

If you want to stop the servers, then press `Ctrl+C`

There are screenshots available in the repo under the Screenshots folder.


