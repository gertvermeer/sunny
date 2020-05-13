#!/bin/bash

if pgrep -f "python server.py" > /dev/null 
then
    echo "Python Server Running"
else
    echo "Server was stopped, now starting"
    cd /home/pi/ledmachine  > /dev/null
    python server.py >> logserver.txt &
    sleep 10
fi
if pgrep -f "python sunny.py" > /dev/null 
then
    echo "Python sunny Running"
else
    echo "Sunny was stopped, now starting"
    cd /home/pi/ledmachine  > /dev/null
    python sunny.py >> logserver.txt &
    sleep 10
fi
if pgrep -f "client.jar" > /dev/null
then
    echo "Client Running"
else
    echo "Client was stopped, now starting"
    cd /home/pi/ledmachine  > /dev/null
    java -jar client.jar >> logclientserver.txt &
fi

