import docker
import utils.scheduler_logger as log

from docker.models.containers import Container


class Scheduler:
    def __init__(self):
        self.__client = docker.from_env()
        self.__containers = []
        self.__logger = log.SchedulerLogger()

        # initial schedule
        # TODO: run containers with initial configuration

    def create(self, container_config):
        """
            Create a new container
        """
        container = self.__client.containers.create(cpuset_cpus=container_config[0],
                                               name=container_config[1],
                                               detach=True,
                                               auto_remove=False,
                                               image=container_config[2],
                                               command=container_config[3])
        self.__containers.append(container)

    def update(self, container : Container, cpu: int):
        """
            Update a container
        """
        if container is None:
            return
        container.update(cpuset_cpus=cpu)

    def remove(self, container : Container):
        """
            Remove a container
        """
        if container is None:
            return
        container.remove()
        

    def pause(self, container : Container):
        """
            Pause a container
        """
        if container is None:
            return
        container.pause()

    def startOrResume(self, container : Container):
        """
            Start or resume (paused) a container
        """
        if container is None:
            return
        
        container.reload()

        if container.status == "paused":
            self.__logger.job_unpause(container.name)
            container.unpause()
        elif container.status == "created":
            self.__logger.job_start(container.name)
            container.start()
        else:
            return
        
    def next(self):
        """
            Schedule the next container to run
        """
        # TODO: implement scheduling policy
        """
            Notes from Parts 1-2:

            Workload      | none cpu  l1d  l1i  l2   llc  memBW
            --------------|------------------------------------
            blackscholes  | 1.00 1.29 1.34 1.54 1.34 1.48 1.31
            canneal       | 1.00 1.23 1.38 1.46 1.30 1.92 1.39
            dedup         | 1.00 1.73 1.28 2.03 1.24 1.98 1.60
            ferret        | 1.00 1.93 1.27 2.31 1.38 2.47 1.97
            freqmine      | 1.00 1.99 1.04 2.04 1.03 1.77 1.58
            radix         | 1.00 1.06 1.11 1.11 1.12 1.52 1.12
            vips          | 1.00 1.73 1.71 1.88 1.68 1.89 1.68

            Parallelization Speedup (threads)
            Workload      | 1       2       4
            --------------|------------------------------------
            dedup         | 1.00    1.74    2.12
            blackscholes  | 1.00    1.70    2.63 
            canneal       | 1.00    1.63    2.43 
            ferret        | 1.00    1.94    2.82 
            freqmine      | 1.00    1.97    3.85 
            radix         | 1.00    2.07    3.96
            vips          | 1.00    1.37    3.28 
        """
        pass
