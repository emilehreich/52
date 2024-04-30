import scheduler
import psutil

# =========================================================================

# ---------------------------------

MEMCACHED_PROCESS_NAME = ""

# ---------------------------------





# =========================================================================

if __name__ == "__main__":
    
    scheduler = scheduler.Scheduler()

    # memcached config
    for process in psutil.process_iter():
        if process.name() == MEMCACHED_PROCESS_NAME:
            memcached = process
            memcached_pid = process.pid
            break
    

