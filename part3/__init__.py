MCPERF_INSTALLATION_COMMAND = "sudo apt-get update && sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32 && sudo -i sh -c 'echo deb-src http://europe-west3.gce.archive.ubuntu.com/ubuntu/ bionic main restricted >> /etc/apt/sources.list' && sudo apt-get update && sudo apt-get install libevent-dev libzmq3-dev git make g++ --yes && sudo apt-get build-dep memcached --yes && git clone https://github.com/eth-easl/memcache-perf-dynamic.git && cd memcache-perf-dynamic && make"

CLIENT_AGENT_A = "client-agent-a"
CLIENT_AGENT_B = "client-agent-b"
CLIENT_MEASURE = "client-measure"

NODE_TWO_CORES = "node-a-2core" # n2d-highcpu-2
NODE_FOUR_CORES = "node-b-4core" # n2d-highmem-4
NODE_EIGHT_CORES = "node-c-8core" # e2-standard-8

MEMCACHED_SERVICE_NAME = "some-memcached"
MEMCACHED_IP = None
NUMBER_RUNS = 3

GCLOUD = "/mnt/c/Users/jfreeman/google-cloud-sdk/bin/gcloud"
MEASURE_SCRIPT = "measure.sh"
RETRIEVE_MEASURES_SCRIPT = "retrieve.sh"

NODES = [CLIENT_AGENT_A, CLIENT_AGENT_B, CLIENT_MEASURE, NODE_TWO_CORES, NODE_FOUR_CORES, NODE_EIGHT_CORES]

MSM_RESULTS_PATH = "/home/jfreeman/52/experiments/part3"