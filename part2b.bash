#!/bin/bash
mkdir -p experiments/part2b

PARSEC_SERVER_ID=$(kubectl get nodes -o wide | grep parsec- | awk '{print substr($1,15)}')

kubectl label nodes parsec-server-$PARSEC_SERVER_ID cca-project-nodetype=parsec

PARSEC_EXPS=("dedup" "blackscholes" "canneal" "ferret" "freqmine" "radix" "vips")
THREADS=("1" "2" "4" "8")

for PARSEC_EXP in ${PARSEC_EXPS[@]}
do
    for THREAD in ${THREADS[@]}
    do
        kubectl create -f parsec-benchmarks/part2b/parsec-$PARSEC_EXP-threads$THREAD.yaml

        bash -x wait_for_jobs.bash

        kubectl logs $(kubectl get pods --selector=job-name=parsec-$PARSEC_EXP --output=jsonpath='{.items[*].metadata.name}') | grep -E 'real|user|sys' >> experiments/part2b/${PARSEC_EXP}_${THREAD}thread\(s\).txt

        kubectl delete jobs --all
    done
done