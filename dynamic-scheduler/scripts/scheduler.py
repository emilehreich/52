import utils.scheduler_logger as log
import utils.batch_applications as batch

from docker.models.containers import Container


class Scheduler:
    def __init__(self, queues : list):

        self.__completed = []
        self.__logger = log.SchedulerLogger()
        self.__mode = 0 

        self.__nq1 = len(queues[0])
        self.__nq2 = len(queues[1])
        self.__nq3 = len(queues[2])

        self.__q1 = iter(queues[0])
        self.__q2 = iter(queues[1])
        self.__q3 = iter(queues[2])

        self.__running_q1 = []
        self.__running_q2 = []
        self.__running_q3 = []

        self.__current_q1: Container = None
        self.__current_q2: Container = None

        self.__available_cpus = 3
        self.__cpus = [0,1,1,1]
        

    def set_mode(self, mode):
        self.__mode = mode
        if mode == 1:
            self.__available_cpus = 2
        
        elif mode == 0:
            self.__available_cpus = 3

        for container in self.__running_q1:
            self.pause(container)
        for container in self.__running_q2:
            self.pause(container)
        for container in self.__running_q3:
            self.pause(container)
            

    def update(self, container : Container, cpuset: list[str]):
        """
            Update a container
        """
        if container is None:
            return
        self.__logger.update_cores(log.Job.get_Job(container.name), cpuset)
        container.update(cpuset_cpus=cpuset)

    def remove(self, container : Container):
        """
            Remove a container
        """
        if container is None:
            return
        self.__logger.job_end(log.Job.get_Job(container.name))
        container.remove()
        

    def pause(self, container : Container):
        """
            Pause a container
        """
        if container is None:
            return
        container.reload()
        self.__logger.job_pause(log.Job.get_Job(container.name))
        if container.status == "running":
            container.pause()

    def startOrResume(self, container : Container):
        """
            Start or resume (paused) a container
        """
        if container is None:
            return
        
        container.reload()

        if container.status == "paused":
            self.__logger.job_unpause(log.Job.get_Job(container.name))
            container.unpause()
        elif container.status == "created":
            print("start : ", container.name )
            job: batch.BatchApplication = batch.BatchApplication.get_job(container.name)
            self.__logger.job_start(log.Job.get_Job(container.name),
                                job.value[0],
                                job.value[4]
                                )
            container.start()
        else:
            return
        

    def next(self, adjust_resources: bool = False):
        """
        Schedule the next container to run
        """
        print("AVAILABLE CPU: ", self.__available_cpus)
        if self.__mode == 0:
            
            # multiprocessor queues
            self.__current_q1, self.__nq1 = self.handle_mp_queue(self.__q1, 
                                                                 self.__nq1, 
                                                                 self.__running_q1, 
                                                                 self.__current_q1, 
                                                                 3, 
                                                                 adjust_resources
                                                                )
            
                                                  
            self.__current_q2, self.__nq2 = self.handle_mp_queue(self.__q2, 
                                                                 self.__nq2, 
                                                                 self.__running_q2, 
                                                                 self.__current_q2, 
                                                                 2, 
                                                                 adjust_resources
                                                                )

            # single processor queue
            if self.__available_cpus >= 1:
                self.handle_sp_queue()
                        

        elif self.__mode == 1:
            # Low Level of Resource Availability

            self.__current_q2, self.__nq2 = self.handle_mp_queue(self.__q2, 
                                                                 self.__nq2, 
                                                                 self.__running_q2, 
                                                                 self.__current_q2, 
                                                                 2, 
                                                                 adjust_resources
                                                                 )
            if self.__available_cpus >= 1:
                self.handle_sp_queue()
            self.__current_q1, self.__nq1 = self.handle_mp_queue(self.__q1, 
                                                                 self.__nq1, 
                                                                 self.__running_q1, 
                                                                 self.__current_q1, 
                                                                 2, 
                                                                 adjust_resources
                                                                 )




    def handle_sp_queue(self):
        """
            Handle the single processor queue
        """
        for c in self.__running_q3:
            if self.__available_cpus >= 1:
                self.startOrResume(c)
                self.__available_cpus -= 1
        c: Container = next(self.__q3, None)
        if c is not None:
            for i in range(1,4):
                if self.__cpus[i] == 1:
                    self.update(c, str(i))
                    self.__cpus[i] = c.name

            self.startOrResume(c)
            self.__running_q3.append(c)
            self.__available_cpus -= 1
    
        self.check_and_handle_exited(c, self.__running_q3, self.__nq3, 1)


    def handle_mp_queue(self, queue, n_queue, running_queue, current, n_cpu, adjust_resources):
        """
            Handle a queue of containers running on multiprocessor
        """
        for c in running_queue:
            if self.__available_cpus >= n_cpu:
                self.startOrResume(c)
                self.__available_cpus -= n_cpu
        if self.__available_cpus >= n_cpu:
            if adjust_resources:
                self.adjust_resources(queue, n_cpu)

            current = self.process_new_container(queue, running_queue, current, n_cpu)
                
            
        current, n_queue = self.check_and_handle_exited(current, running_queue, n_queue, n_cpu)
        return current, n_queue

    def adjust_resources(self, queue, n_cpu):
        if n_cpu == 3:
            cpuset = "1,2,3"
        elif n_cpu == 2:
            cpuset = "2,3"
        for c in queue:
            self.update(c, cpuset)

    def process_new_container(self, queue, running_queue: list, current: Container, n_cpu):
        c = next(queue, None)
        if c is not None:
            self.startOrResume(c)
            running_queue.append(c)
            self.__available_cpus -= n_cpu
            return c
        else:
            return current

    def check_and_handle_exited(self, current: Container, running_queue: list[Container], n_queue, n_cpu):
        for container in running_queue:
            container.reload()
            if container.status == "exited":
                for c in range(1,4):
                    if self.__cpus[c] == container.name:
                        self.__cpus[c] = 1
                running_queue.remove(container)
                self.remove(container)
                n_queue -= 1
                self.__completed.append(current)
                current = None
                self.__available_cpus += n_cpu
        return current, n_queue
        
                
        