
#!/usr/bin/env python3

import subprocess
import re
import os
import sys
import numpy as np
import time

import argparse
# run "export KOPS_STATE_STORE=gs://cca-eth-2024-group-052-jfreeman" on the os
os.environ["KOPS_STATE_STORE"] = "gs://cca-eth-2024-group-052-jfreeman"
# alias gsutil=/mnt/c/Users/jfreeman/google-cloud-sdk/bin/gsutil
GSUTIL = "/mnt/c/Users/jfreeman/google-cloud-sdk/bin/gsutil"

from part3 import *
PWD = "/home/jfreeman/52/part3"
os.chdir(PWD)

def main(args):  
    if args.restart_memcached_only:
        print("Restarting memcached...")
        sh = subprocess.run(f"""kubectl delete pods --all""", shell=True, capture_output=True)
        sh = subprocess.run(f"""kubectl create -f memcache-t1-cpuset-part3.yaml""", shell=True, capture_output=True)

        print(f"Waiting for memcached to start...")
        MEMCACHED_START = False
        while(not MEMCACHED_START):
            sh = subprocess.run(f"""kubectl get pods | grep {MEMCACHED_SERVICE_NAME}""", shell=True, capture_output=True)
            
            if("Running" in sh.stdout.decode("utf-8")):
                MEMCACHED_START = True
            time.sleep(1)
        print("Memcached restarted!")
    if args.delete_cluster or args.restart_cluster:
        print("Deleting any trace of a previous cluster...")
        print("\r Deleting cluster...")
        sh = subprocess.run("kops delete cluster --name part3.k8s.local --yes", shell=True, capture_output=True)
        print("\r Deleting bucket...")
        sh = subprocess.run(f"{GSUTIL} rm -r gs://cca-eth-2024-group-052-jfreeman/part3.k8s.local", shell=True, capture_output=True)
        print("\r Deleting Subnetwork...")
        sh = subprocess.run(f"{GCLOUD} dns managed-zones delete part3-k8s-local --project=cca-eth-2024-group-052 --quiet", shell=True, capture_output=True)
        print("Cluster deleted.")
        if not args.restart_cluster:
            sys.exit(0)
    if(args.init_cluster or args.restart_cluster):
        print("Initializing cluster...", end="")
        sh = subprocess.run("kops create -f part3.yaml", shell=True, capture_output=True)
        # check that the output contains "To deploy these resources, run: "<command to extract> endline. This is a sign that the cluster was created successfully
        if not "To deploy these resources, run: " in sh.stdout.decode("utf-8"):
            print("\nCluster failed to initialize. Exiting...")
            sys.exit(1)
        else:
            # add a checkmark to the output
            next_command = re.search(r"To deploy these resources, run: (.*)", sh.stdout.decode("utf-8")).group(1)
            print("✓")
        sh = subprocess.run(next_command, shell=True, capture_output=True)

        print("Waiting for cluster to be ready...")
        sh = subprocess.run("kops validate cluster --name part3.k8s.local --wait 10m", shell=True, capture_output=False)
        
        if not sh.returncode == 0:
            print("Cluster failed to initialize. Deleting cluster and exiting..")
            sh = subprocess.run("kops delete cluster --name part3.k8s.local --yes", shell=True, capture_output=True)
            print("Cluster deleted.")

            sys.exit(1)
        print("Cluster is ready!")
    



    print("Getting node information...")
    # Execute the kubectl get nodes -o wide command
    result = subprocess.run(["kubectl", "get", "nodes", "-o", "wide"], capture_output=True, text=True)

    # Split the output into lines
    lines = result.stdout.split('\n')

    # Initialize an empty dictionary to store the final result
    final_result = {}

    # Iterate over each line
    for line in lines:
        # For each node
        for name in NODES:
            # If the node name is in the line
            if name in line:
                match = re.search(rf"({name}-\w+)\s+\w+\s+\w+\s+\w+\s+[\w.]+\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)", line)
                if match:
                    final_result[name] = {"NAME": match.group(1), "INTERNAL_IP": match.group(2), "EXTERNAL_IP": match.group(3)}

    
    #Example of one KV pair: {'client-agent-a': {'NAME': 'client-agent-a-2core', 'INTERNAL_IP': ..., 'EXTERNAL_IP': ...}}
    node_infos = final_result

    if(args.init_vms or args.init_cluster or args.restart_cluster):
        print("Configuring client and measure nodes...")

        for node in [CLIENT_AGENT_A, CLIENT_AGENT_B, CLIENT_MEASURE]:
            print(f"Configuring {node}...")


            ssh_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[node]["NAME"]} --command=\"{MCPERF_INSTALLATION_COMMAND}\""""

            print(f"sending command: {ssh_command}")
            sh = subprocess.run(ssh_command, shell=True)
            print(f"Configured {node}!")
            
        print(f"Starting memcached")
        sh = subprocess.run(f"""kubectl delete pods --all""", shell=True, capture_output=True)
        sh = subprocess.run(f"""kubectl create -f memcache-t1-cpuset-part3.yaml""", shell=True, capture_output=True)

        print(f"Waiting for memcached to start...")
        MEMCACHED_START = False
        while(not MEMCACHED_START):
            sh = subprocess.run(f"""kubectl get pods | grep {MEMCACHED_SERVICE_NAME}""", shell=True, capture_output=True)
            
            if("Running" in sh.stdout.decode("utf-8")):
                MEMCACHED_START = True
            time.sleep(1)
        print(f"Memcached started!")
        print("Cluster config done!")
            

    

    #Getting the IP of the memcached service
    sh = subprocess.run(f"""kubectl get pods -o wide | grep {MEMCACHED_SERVICE_NAME}""", shell=True, capture_output=True)
    # sh.stdout.decode("utf-8") should be something like "some-memcached-5f8b7b7b7b-5j2j2 1/1 Running 0 2m
    MEMCACHED_IP = sh.stdout.decode("utf-8").split()[5] #IP of service is sixth element in the output 

    agent_a_launch_command = "cd memcache-perf-dynamic && ./mcperf -T 2 -A"
    agent_b_launch_command = "cd memcache-perf-dynamic && ./mcperf -T 4 -A"
    agent_msmt_launch_command = f"""cd memcache-perf-dynamic && ./mcperf -s {MEMCACHED_IP} --loadonly && \
                ./mcperf -s {MEMCACHED_IP} -a {node_infos[CLIENT_AGENT_A]["INTERNAL_IP"]} -a {node_infos[CLIENT_AGENT_B]["INTERNAL_IP"]} --noload -T 6 -C 4 -D 4 -Q 1000 -c 4 -t 10 --scan 30000:30500:5"""
   
    retrieve_a_command = f"""{GCLOUD} compute scp ubuntu@{node_infos[CLIENT_AGENT_A]["NAME"]}:/tmp/output-agent-a.txt {MSM_RESULTS_PATH}/results-agent-a.txt"""
    retrieve_b_command = f"""{GCLOUD} compute scp ubuntu@{node_infos[CLIENT_AGENT_B]["NAME"]}:/tmp/output-agent-b.txt {MSM_RESULTS_PATH}/results-agent-b.txt"""
    retrieve_msmt_command = f"""{GCLOUD} compute scp ubuntu@{node_infos[CLIENT_MEASURE]["NAME"]}:/tmp/results.txt {MSM_RESULTS_PATH}/results-measure.txt"""
    
    print(f"""To retrieve measurement results run the following commands in order:
        1. {retrieve_a_command}
        2. {retrieve_b_command}
        3. {retrieve_msmt_command}""")
    # Output commands as a script in a single line
    with open(f"{RETRIEVE_MEASURES_SCRIPT}", "w") as f:
        f.write(f"""#!/bin/bash\n{retrieve_a_command}\n{retrieve_b_command}\n{retrieve_msmt_command}\n""")
    print(f"Commands written to {RETRIEVE_MEASURES_SCRIPT}")


    # Login and launch commands are combined. Their outputs are redirected into text files under /tmp folder.
    agent_a_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[CLIENT_AGENT_A]["NAME"]} --command='{agent_a_launch_command}' > /tmp/output-agent-a.txt"""
    agent_b_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[CLIENT_AGENT_B]["NAME"]} --command='{agent_b_launch_command}' > /tmp/output-agent-b.txt"""
    agent_msmt_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[CLIENT_MEASURE]["NAME"]} --command='{agent_msmt_launch_command}' > /tmp/output-measure.txt"""
    

    agent_a_login_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[CLIENT_AGENT_A]["NAME"]}"""
    agent_b_login_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[CLIENT_AGENT_B]["NAME"]}"""
    agent_msmt_login_command = f"""{GCLOUD} compute ssh ubuntu@{node_infos[CLIENT_MEASURE]["NAME"]}"""
 
    print(f"""To launch measurement by hand run the following commands in order:
        1. {agent_a_login_command}
        2. {agent_a_command}
        3. {agent_b_login_command}
        4. {agent_b_command}
        5. {agent_msmt_login_command}
        6. {agent_msmt_command}""")
    
    
    # Output commands as a script in a single line
    with open(f"{MEASURE_SCRIPT}", "w") as f:
        f.write(f"""#!/bin/bash\n{agent_a_command}\n{agent_b_command}\n{agent_msmt_command}\n""")
    print(f"Commands written to {MEASURE_SCRIPT}")

   


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--delete_cluster", action="store_true")
    parser.add_argument("--init_cluster", help="Initialize the cluster. If already running, deletes cluster and starts a new one.",
                        action="store_true")
    parser.add_argument("--init_vms", help="Installs mcperf on the vms. If init_cluster is set, this is done automatically.", action="store_true")
    parser.add_argument("--restart_cluster", help="Restarts the cluster. Deletes and creates a new one.", action="store_true")
    parser.add_argument("--restart_memcached_only", help="Restarts the memcached service only.", action="store_true")
    args = parser.parse_args()
    main(args)