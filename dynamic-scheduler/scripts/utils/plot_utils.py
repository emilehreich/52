JOBS = ["blackscholes", "canneal", "dedup", "ferret", "freqmine", "radix", "vips"]


class Segment:
    def __init__(self, start, core):
        self.start = start
        self.end = -1
        self.core = core


class Job:
    def __init__(self, name):
        self.name = name
        self.cores = []
        self.active = {}
        self.segments = []
        self.running = False

    def start(self, time, cores):
        self.running = True
        self.cores = cores
        for core in cores:
            self.active[core] = Segment(time, core)

    def update_cores(self, time, cores):
        self.end(time)
        self.start(time, cores)

    def pause(self, time):
        self.end(time)

    def unpause(self, time):
        self.start(time, self.cores)

    def end(self, time):
        self.running = False
        next_active = self.active.copy()
        for segment in self.active.values():
            segment.end = time
            self.segments.append(segment)
            next_active.pop(segment.core)
        self.active = next_active



import dateutil.parser
from math import floor

JOBS: set = {
    "blackscholes",
    "canneal",
    "dedup",
    "ferret",
    "freqmine",
    "radix",
    "vips",
}


def extract_times(part):
    runs = {}

    for i in range(3):
        with open(
            f"../Q{part}/jobs_{i + 1}.txt", "r"
        ) as file:
            starttime = None
            endtime = None
            for line in file.readlines():
                tokens = line.replace("\n", "").split(" ")

                time = floor(
                    dateutil.parser.isoparse(tokens[0] + "Z").timestamp() * 1000
                )  # POSIX timestamp (float in seconds)
                cmd = tokens[1]
                job = tokens[2]

                if job == "scheduler" and cmd == "start":
                    starttime = time
                elif job == "scheduler" and cmd == "end":
                    endtime = time

        runs[i + 1] = (starttime, endtime)
    return runs


def extract_segments(part):
    runs = {}

    for i in range(3):
        with open(
            f"../Q{part}/jobs_{i + 1}.txt", "r"
        ) as file:
            jobs = {}
            for line in file.readlines():
                tokens = line.replace("\n", "").split(" ")

                time = floor(
                    dateutil.parser.isoparse(tokens[0] + "Z").timestamp() * 1000
                )  # POSIX timestamp (float in seconds)
                cmd = tokens[1]
                job = tokens[2]

                if job not in JOBS:
                    continue

                if cmd == "start":
                    if job in jobs:
                        print("Error: Found invalid start")
                        continue

                    cores = tokens[3][1:-1].split(",")
                    new_job = Job(job)
                    new_job.start(time, cores)
                    jobs[job] = new_job

                elif cmd == "update_cores":
                    if not job in jobs or not jobs[job].running:
                        print("Error: Found invalid cores update")
                        continue

                    cores = tokens[3][1:-1].split(",")
                    jobs[job].update_cores(time, cores)

                elif cmd == "pause":
                    if not job in jobs or not jobs[job].running:
                        print("Error: Found invalid pause")
                        continue

                    jobs[job].pause(time)

                elif cmd == "unpause":
                    if not job in jobs or jobs[job].running:
                        print("Error: Found invalid unpause")
                        continue

                    jobs[job].unpause(time)
                elif cmd == "end":
                    if not job in jobs or not jobs[job].running:
                        print("Error: Found invalid end")
                        continue

                    jobs[job].end(time)

        runs[i + 1] = jobs
    return runs


def count_cores(part, run):
    with open(f"../Q{part}/jobs_{run}.txt", "r") as file:
        lines = file.readlines()
    times = list()
    counts = list()
    for line in lines:
        if 'memcached' in line:
                tokens = line.split()
                cores = tokens[3]
                time = floor(dateutil.parser.isoparse(tokens[0] + "Z").timestamp() * 1000)
                cores = cores.strip('[]').split(',')
                count = 1 if len(cores) == 1 else 2
                times.append(time)
                counts.append(count)
    return times, counts


def extract_results(part, interval):
    runs = {}
    for i in range(3):
        data = []

        with open(
            f"../Q{part}/mcperf_{i + 1}.txt", "r"
        ) as file:
            lines = file.readlines()

        # Find the index of the start timestamp line
        timestamp_line_index = None
        for index, line in enumerate(lines):
            if line.startswith("Timestamp start"):
                timestamp_line_index = index
                break

        # Extract the start timestamp
        if timestamp_line_index is not None:
            start = int(lines[timestamp_line_index].split()[-1])

        # Find the index of the headers line
        headers_line_index = None
        for index, line in enumerate(lines):
            if line.startswith("#type"):
                headers_line_index = index
                break

        # Extract the relevant columns
        if headers_line_index is not None:
            headers = lines[headers_line_index].split()
            p95_index = headers.index("p95")
            qps_index = headers.index("QPS")

            # Iterate over the data lines and extract the values
            line_number = 0
            for line in lines[headers_line_index + 1 :]:
                if line.startswith("read"):
                    values = line.split()
                    p95 = float(values[p95_index]) / 1000.0
                    qps = float(values[qps_index])
                    data.append((qps, p95, start + line_number * interval))
                    line_number += 1
        runs[i + 1] = data
    return runs