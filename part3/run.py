
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
    subprocess.run("kubectl create -f ../parsec-benchmarks/part3/parsec-radix.yaml", shell=True, capture_output=True)
    subprocess.run("kubectl create -f ../parsec-benchmarks/part3/parsec-vips.yaml", shell=True, capture_output=True)

    # wait that the vips job is in "Running" STATUS
    print("Waiting for radix to start...")
    job_started = False
    while not job_started:
        sh = subprocess.run("kubectl get pods | grep parsec-radix", shell=True, capture_output=True)
        if "Running" in sh.stdout.decode("utf-8"):
            job_started = True
            print(sh.stdout.decode("utf-8"))
            print("radix started!")
        time.sleep(0.1)

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-dedup.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-canneal.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-ferret.yaml", shell=True, capture_output=True)
        executor.submit(subprocess.run, "kubectl create -f ../parsec-benchmarks/part3/parsec-freqmine.yaml", shell=True, capture_output=True)
    


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

    def wait_for_job_completions(jobs):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for job in jobs:
                executor.submit(wait_for_job_completion, job)
    
    wait_for_job_completions(["ferret", "canneal"])
    
    # run blackscholes once canneal and ferret are done.

    subprocess.run("kubectl create -f ../parsec-benchmarks/part3/parsec-blackscholes.yaml", shell=True, capture_output=True)

    
    print("Waiting for jobs to finish...")

    JOBS_FINISHED = False
    while(not JOBS_FINISHED):
        sh = subprocess.run("kubectl get jobs", shell=True, capture_output=True)
        if(not ("0/1" in sh.stdout.decode("utf-8"))):
            JOBS_FINISHED = True
        # check for errors
        
        time.sleep(0.1)
    print("Jobs finished!")






def main(args):
    
    for _ in range(1,NUMBER_RUNS+1):
        if(not args.process_only):
            run_benchmarks_and_wait()
            time.sleep(0.1)

        print("Getting results...")
        sh = subprocess.run(f"kubectl get pods -o json > ../experiments/part3/run{_}/pods.json", shell=True, capture_output=True)
        sh = subprocess.run(f"python3 ../get_time.py ../experiments/part3/run{_}/pods.json > ../experiments/part3/run{_}/processed_results.txt", shell=True, capture_output=True)
        print("Done!")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--process_only", action="store_true")
    parser.add_argument("--delete_cluster", action="store_true") 
    args = parser.parse_args()
    main(args)




