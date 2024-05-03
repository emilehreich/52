import matplotlib.pyplot as plt
import os
import re
import numpy as np

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

    plt.plot(threads, speedup, marker='o', markersize=1.5, label=experiment, linewidth=0.01)

experiments = ["dedup", "blackscholes", "canneal", "ferret", "freqmine", "radix", "vips"]

for experiment in experiments:
    plot_graph(experiment)

threads = range(1,9)
# Amdahl's law
P = 0.875
threads = np.linspace(1, 8, 500) 
amdahl_speedup = [1 / ((1-P) + P/thread) for thread in threads]
plt.plot(threads, amdahl_speedup, marker=None, label='Amdahl\'s law (P=0.9)', linestyle= ':', linewidth=1)
    
plt.plot(threads, threads, marker=None, label='Linear Speedup', linestyle=':', linewidth=1)


plt.xlabel('Number of Threads')
plt.ylabel('Speedup')
plt.legend(fontsize=9)
plt.ylim(0.75,7.5)
plt.grid(True)
plt.savefig("part2b.pdf")