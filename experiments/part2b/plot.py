import matplotlib.pyplot as plt
import os
import re

def get_avg_real_time(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        print(lines, re.findall(r"[-+]?\d*\.\d+|\d+", lines[-1]))
        avg_real_time = float(re.findall(r"[-+]?\d*\.\d+|\d+", lines[-1])[2])
        return avg_real_time

def plot_graph(experiment):
    threads = [1, 2, 4, 8]
    times = []
    for thread in threads:
        file_name = f'{experiment}_{thread}thread(s).txt'
        avg_time = get_avg_real_time(file_name)
        times.append(avg_time)

    speedup = [times[0]/time for time in times]

    plt.plot(threads, speedup, marker='.', label=experiment, linewidth=0.01)

plt.plot([1, 2, 4, 8], [1, 2, 4, 8], linestyle="dashed", color="0.8", label="linear")
experiments = ["dedup", "blackscholes", "canneal", "ferret", "freqmine", "radix", "vips"]

for experiment in experiments:
    plot_graph(experiment)

plt.xlabel('Number of Threads')
plt.ylabel('Speedup')
# plt.title('Speedup vs Number of Threads')
plt.legend()
plt.grid(True)
plt.savefig("part2b.pdf", bbox_inches='tight')
