import scheduler
import psutil
import time
import os
import docker
import utils.scheduler_logger as log
import utils.batch_applications as batch
# =========================================================================

# ---------------------------------

MEMCACHED_PROCESS_NAME = "memcached"
CPU_THRESH = 90

MEMCACHED_LOAD = 0 # 0: low, 1: high

# ---------------------------------

def update_memcached(cpu_set, memcached_pid):
    os.system('sudo taskset -acp ' + cpu_set + ' ' + str(memcached_pid) )

def create(container_config):
        """
            Create a new container
        """
        client = docker.from_env()
        container = client.containers.create(cpuset_cpus=container_config[0],
                                               name=container_config[1],
                                               detach=True,
                                               auto_remove=False,
                                               image=container_config[2],
                                               command=container_config[3])
        return container

# =========================================================================

if __name__ == "__main__":
    
    logger = log.SchedulerLogger()
    jobs = batch.BatchApplication
    
    # memcached config
    for process in psutil.process_iter():
        if process.name() == MEMCACHED_PROCESS_NAME:
            memcached = process
            memcached_pid = process.pid
            break

    update_memcached("0", memcached_pid)

    p_memcached = psutil.Process(memcached_pid)
    logger.job_start(log.Job.MEMCACHED, [0], 2)

    # initialize queues configurations
    queues = []
    queue_1 = [create(jobs.FREQMINE.value),
                create(jobs.VIPS.value) ]
    
    queue_2 = [create(jobs.FERRET.value),
               create(jobs.RADIX.value)]
    
    queue_3 = [create(jobs.BLACKSHOLES.value), 
               create(jobs.CANNEAL.value),
               create(jobs.DEDUP.value)]

    queues.append(queue_1)
    queues.append(queue_2)
    queues.append(queue_3)

    # initialize scheduler
    s = scheduler.Scheduler(queues)

    memcached_percent = 0
    p_memcached.cpu_percent() # ignore first measurement
    
    adjust_resources = False
    

    counter = 0

    while True:
        time.sleep(2)  # Sleep for 2 seconds, the basic cycle time for the loop

        # monitor CPU utilization
        s_memcached_percent = memcached_percent
        memcached_percent = p_memcached.cpu_percent()

        print(memcached_percent)
        ## -- control scheduling --

        # Initialize the adjust_resources flag to False at each iteration
        adjust_resources = False

        # Every 5 iterations of 2 seconds each (10 seconds total), adjust resources
        if counter % 5 == 0:
            # adjust memcached resources
            if memcached_percent > CPU_THRESH and abs(s_memcached_percent - memcached_percent) > 0 and MEMCACHED_LOAD == 0:
                logger.update_cores(log.Job.MEMCACHED, ["0,1"])
                update_memcached("0,1", memcached_pid)
                MEMCACHED_LOAD = 1
                print("changing mode")
                s.set_mode(MEMCACHED_LOAD)
                adjust_resources = True
            elif memcached_percent <= CPU_THRESH and abs(s_memcached_percent - memcached_percent) > 0 and MEMCACHED_LOAD == 1:
                logger.update_cores(log.Job.MEMCACHED, ["0"])
                update_memcached("0", memcached_pid)
                MEMCACHED_LOAD = 0
                print("changing mode")
                s.set_mode(MEMCACHED_LOAD)
                adjust_resources = True

        # Always call s.next() with the state of adjust_resources, whether it was changed or not
        s.next(adjust_resources=adjust_resources)

        # Increment the counter
        counter += 1