#!/bin/bash

CLIENT_MEASURE_ID=$(kubectl get nodes -o wide | grep client-measure- | awk '{print substr($1,16)}')
INTERNAL_AGENT_IP=$(kubectl get nodes -o wide | grep client-agent- | awk '{print $6}')
MEMCACHED_IP=$(kubectl get pods -o wide | grep -m 1 memcache-server | awk '{print $6}')

for EXP in ibench-cpu ibench-l1d ibench-l1i ibench-l2 ibench-llc ibench-membw
do
    echo "Starting experiment for: $EXP"

    echo "Creating pods for: $EXP"
    kubectl create -f interference/$EXP.yaml


    echo "Logging into client-measure-$CLIENT_MEASURE_ID"
    gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-measure-$CLIENT_MEASURE_ID --zone europe-west3-a --command "cd ~/memcache-perf && ./mcperf -s $MEMCACHED_IP -a $INTERNAL_AGENT_IP --noload -T 16 -C 4 - 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> exp-$EXP.txt && ./mcperf -s $MEMCACHED_IP -a $INTERNAL_AGENT_IP --noload -T 16 -C 4 - 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> exp-$EXP.txt && ./mcperf -s $MEMCACHED_IP -a $INTERNAL_AGENT_IP --noload -T 16 -C 4 - 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> exp-$EXP.txt"

    echo "Logging out from client-measure-$CLIENT_MEASURE_ID"
	
    sleep 5

    echo "Deleting pods for: $EXP"
    kubectl delete pods $EXP

    echo "Copying results..."
    gcloud compute scp --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-measure-$CLIENT_MEASURE_ID:~/memcache-perf/exp-$EXP.txt ./reults1/exp-$EXP.txt --zone europe-west3-a

    echo "Finished experiment for: $EXP"
done
