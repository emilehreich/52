#!/bin/bash
mkdir -p experiments/part2a

PARSEC_SERVER_ID=$(kubectl get nodes -o wide | grep parsec- | awk '{print substr($1,15)}')

kubectl label nodes parsec-server-$PARSEC_SERVER_ID cca-project-nodetype=parsec

IBENCH_EXPS=("no_ibench_interference" "cpu" "l1d" "l1i" "l2" "llc" "membw")
PARSEC_EXPS=("dedup" "blackscholes" "canneal" "ferret" "freqmine" "radix" "vips")

for IBENCH_EXP in ${IBENCH_EXPS[@]}
do
    if [ "$IBENCH_EXP" != "no_ibench_interference" ]
    then
        kubectl create -f interference/ibench-$IBENCH_EXP.yaml
        sleep 5 # making sure interference has started.
    fi

    for PARSEC_EXP in ${PARSEC_EXPS[@]}
    do
        
        kubectl create -f parsec-benchmarks/part2a/parsec-$PARSEC_EXP.yaml

        bash -x wait_for_jobs.bash

        kubectl logs $(kubectl get pods --selector=job-name=parsec-$PARSEC_EXP --output=jsonpath='{.items[*].metadata.name}') | grep -E 'real|user|sys' >> experiments/part2a/${PARSEC_EXP}_vs_${IBENCH_EXP}.txt

        kubectl delete jobs --all
        
    done

    kubectl delete pods --all
done