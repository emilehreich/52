import scheduler
import psutil
import time
import os

# =========================================================================

# ---------------------------------

MEMCACHED_PROCESS_NAME = ""
CPU_THRESH = 0

# ---------------------------------

def update_memcached(n_cpu, memcached_pid):
    os.system('taskset -acp ' + str(n_cpu) + ' ' + memcached_pid + ' >/dev/null')



# =========================================================================

if __name__ == "__main__":
    
    scheduler = scheduler.Scheduler()

    # memcached config
    for process in psutil.process_iter():
        if process.name() == MEMCACHED_PROCESS_NAME:
            memcached = process
            memcached_pid = process.pid
            break

    p_memcached = psutil.Process(memcached_pid)

    # initialize queues configurations
    queues = []
    queue_1 = []
    queue_2 = []
    queue_3 = []

    # create scheduler
    s = scheduler.Scheduler(queues)


    # Daemon
    while True:
        time.sleep(0.5)

        # monitor CPU utilization
        memcached_percent = p_memcached.cpu_percent()
        cpu_percent = psutil.cpu_percent(interval=None, percpu=True)

        # control scheduling

    

