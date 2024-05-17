
#!/usr/bin/env python3

import subprocess
import re
import os
import sys
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
import argparse

from part3 import *
os.environ["KOPS_STATE_STORE"] = "gs://cca-eth-2024-group-052-jfreeman"

pwd = "/home/jfreeman/52/part3"
os.chdir(pwd)

def wait_for_job_completion(job_name):
    print(f"Waiting for {job_name} to finish...")
    job_finished = False
    while not job_finished:
        sh = subprocess.run(f"kubectl get jobs | grep parsec-{job_name}", shell=True, capture_output=True)
        if ("Terminating" in sh.stdout.decode("utf-8") or "Completed" in sh.stdout.decode("utf-8") or not ("0/1" in sh.stdout.decode("utf-8"))) and sh.stdout.decode("utf-8") != "":
            print(sh.stdout.decode("utf-8"))
            job_finished = True
        if("Error" in sh.stdout.decode("utf-8")):
            print("Error in job execution. Exiting...")
            sys.exit(1)

        time.sleep(0.1)
    print(f"{job_name} finished!")


def run_benchmarks_and_wait():
    print("Deleting past jobs (and pods, except some-memcached)...")
    sh = subprocess.run("kubectl delete jobs --all", shell=True, capture_output=True)

    sh = subprocess.run("kubectl get pods | grep -v some-memcached | awk '{print $1}' | xargs kubectl delete pod", shell=True, capture_output=True)

    # wait until there are no jobs with status "terminating"
    print("Waiting for jobs to terminate...")
    jobs_terminating = True
    while(jobs_terminating):
        sh = subprocess.run("kubectl get pods", shell=True, capture_output=True)
        if not ("Terminating" in sh.stdout.decode("utf-8")):
            print(sh.stdout.decode("utf-8"))
            jobs_terminating = False
        time.sleep(1)


    print("Launching the jobs...")
    # use a multi-threaded approach to run all the benchmarks at the same time

    # wait that the vips job is in "Running" STATUS
    print("Waiting for vips to start...")
    subprocess.run("kubectl create -f ../parsec-benchmarks/part3/parsec-freqmine.yaml", shell=True, capture_output=True)
    job_started = False
    while not job_started:
        sh = subprocess.run("kubectl get pods | grep parsec-freqmine", shell=True, capture_output=True)
        if "Running" in sh.stdout.decode("utf-8"):
            job_started = True
            print(sh.stdout.decode("utf-8"))
            print("freqmine started!")
        time.sleep(0.1)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-vips.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-radix.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-canneal.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-ferret.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-blackscholes.yaml", shell=True, capture_output=True)
    
    print("Waiting for radix to finish to run dedup")
    wait_for_job_completion("radix")
    print("radix finished!")
    print("Running dedup...")
    subprocess.run("kubectl create -f ../parsec-benchmarks/part3/parsec-dedup.yaml", shell=True, capture_output=True)


    with ThreadPoolExecutor(max_workers=7) as executor:
        executor.submit(wait_for_job_completion, "dedup")
        executor.submit(wait_for_job_completion, "canneal")
        executor.submit(wait_for_job_completion, "ferret")
        executor.submit(wait_for_job_completion, "freqmine")
        executor.submit(wait_for_job_completion, "blackscholes")
        executor.submit(wait_for_job_completion, "vips")
        executor.submit(wait_for_job_completion, "radix")

        
        
        time.sleep(0.1)
    print("Jobs finished!")
    # send notification to the OS
    subprocess.run("notify-send 'Jobs finished!'", shell=True, capture_output=True)






def main(args):
    
    for _ in range(1,NUMBER_RUNS+1):
        if(not args.process_only):
            run_benchmarks_and_wait()
            time.sleep(0.1)

        print("Getting results...")
        sh = subprocess.run(f"kubectl get pods -o json > ../experiments/part3/pods.json", shell=True, capture_output=True)
        sh = subprocess.run(f"python3 ../get_time.py ../experiments/part3/pods.json > ../experiments/part3/processed_results.txt", shell=True, capture_output=True)
        print("Done!")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--process_only", action="store_true")
    parser.add_argument("--delete_cluster", action="store_true") 
    args = parser.parse_args()
    main(args)




