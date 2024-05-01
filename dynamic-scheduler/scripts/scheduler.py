import docker
import utils.scheduler_logger as log

from docker.models.containers import Container


class Scheduler:
    def __init__(self, queues : list):
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
        pass
