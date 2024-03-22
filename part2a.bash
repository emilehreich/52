#!/bin/bash
mkdir -p experiments/part2a

PARSEC_SERVER_ID=$(kubectl get nodes -o wide | grep parsec- | awk '{print substr($1,15)}')

kubectl label nodes parsec-server-$PARSEC_SERVER_ID cca-project-nodetype=parsec

for IBENCH_EXP in cpu l1d l1i l2 llc membw
do
    for PARSEC_EXP in dedup blackscholes canneal ferret freqmine radix vips
    do
        kubectl create -f interference/ibench-$IBENCH_EXP.yaml

        sleep 5 # making sure interference has started.

        kubectl create -f parsec-benchmarks/part2a/parsec-$PARSEC_EXP.yaml

        sleep 60 # just to be sure that it is completed

        kubectl logs $(kubectl get pods --selector=job-name=parsec-$PARSEC_EXP --output=jsonpath='{.items[*].metadata.name}') > experiments/part2a/${PARSEC_EXP}_vs_${IBENCH_EXP}.txt
        echo \n >> experiments/part2a/${PARSEC_EXP}_vs_${IBENCH_EXP}.txt
        kubectl get jobs >> experiments/part2a/${PARSEC_EXP}_vs_${IBENCH_EXP}.txt

        kubectl delete jobs --all

        kubectl delete pods --all
    done

    
done
