#!/bin/bash

for EXP in ibench-cpu ibench-cpu ibench-l1d ibench-l1i ibench-l2 ibench-llc ibench-membw
do
    echo "Starting experiment for: $EXP"
    
    echo "Creating pods for: $EXP"
    kubectl create -f interference/$EXP.yaml
    
    echo "Getting pods..."
    kubectl get pods -o wide
    
    echo "Logging into client-measure-d8fb"
    /mnt/c/Users/jfreeman/google-cloud-sdk/bin/gcloud compute ssh --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-measure-d8fb --zone europe-west3-a --command "cd ~/memcache-perf && ./mcperf -s 100.96.3.2 -a 10.0.16.5 --noload -T 16 -C 4 - 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> exp-$EXP.txt && ./mcperf -s 100.96.3.2 -a 10.0.16.5 --noload -T 16 -C 4 - 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> exp-$EXP.txt && ./mcperf -s 100.96.3.2 -a 10.0.16.5 --noload -T 16 -C 4 - 4 -Q 1000 -c 4 -t 5 -w 2 --scan 5000:55000:5000 >> exp-$EXP.txt"
   
    echo "Logging out from client-measure-d8fb"
    
    echo "Deleting pods for: $EXP"
    kubectl delete pods $EXP
    
    echo "Copying results..."
    /mnt/c/Users/jfreeman/google-cloud-sdk/bin/gcloud compute scp --ssh-key-file ~/.ssh/cloud-computing ubuntu@client-measure-d8fb:~/memcache-perf/exp-$EXP.txt ./52 --zone europe-west3-a

    echo "Finished experiment for: $EXP"
done
