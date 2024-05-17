import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import janitor

# Get a list of all txt files in the current directory
latency_files = glob.glob('memcachedT?C?_latency.txt')
cpu_files = glob.glob('memcachedT?C?_cpu.txt')

# Define column headers
headers = ['type', 'avg', 'std', 'min', 'p5', 'p10', 'p50', 'p67', 'p75', 'p80', 'p85', 'p90', 'p95', 'p99', 'p999', 'p9999', 'QPS', 'target', 'ts_start', 'ts_end'] 

# Okabe-Ito color palette                 
#           black     orange     skyblue  bluishgreen red-purple    gray
colors = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#CC79A7", "#999999"] 
markers = ["v", "s", "^", "o", "o", "o"]
plotname = ["part4_q1d_2core.pdf","part4_q1d_1core.pdf"]
index = 0
# Loop through the files list and plot the data from each file
for lat_file, cpu_file in zip(latency_files, cpu_files):
    plt.figure(index, figsize=(15, 9))
    # Load data from file into a pandas DataFrame
    print(lat_file, cpu_file)
    df = pd.read_csv(lat_file, delim_whitespace=True, comment='#', names=headers)
    cpu = pd.read_csv(cpu_file, sep='|', header=None, names=['cpu_usage', 'core1', 'core2', 'core3', 'core4', 'timestamp'])
    cpu.timestamp = (cpu.timestamp * 1e3).astype(int)
    df = df.conditional_join(
      cpu, 
      ('ts_start', 'timestamp', '<='), 
      ('ts_end', 'timestamp', '>='),
      right_columns=['timestamp','cpu_usage'],
      keep='first'
    )
    # Convert p95 from microseconds to milliseconds
    df['p95'] = df['p95'] / 1e3
    df['cpu_usage'] = df['cpu_usage'] * (index+1) / 100

    # Group the DataFrame by 'QPS' and compute the mean of 'p95'
    p95_mean = df.groupby('target')[['QPS', 'p95']].mean()
    cpu_mean = df.groupby('target')[['QPS', 'cpu_usage']].mean()
    plt.plot(p95_mean['QPS'], p95_mean['p95'], label="Latency", linestyle='--', linewidth=1.0, color=colors[1], marker=markers[0], markersize=10, fillstyle='none')
    plt.plot(cpu_mean['QPS'], cpu_mean['cpu_usage'], label="CPU Usage", linestyle='--', linewidth=1.0, color=colors[2], marker=markers[1], markersize=10, fillstyle='none')
    plt.plot(range(130000), [1]*130000, linestyle='--', linewidth=2.0, color=colors[-1])

    # Set the size of the text
    text_size = 12

    # labeling axes
    plt.xlabel('Average Queries per Second $(s^{-1})$', fontsize=text_size)
    plt.ylabel('Average P95 Latency $(ms)$', fontsize=text_size)
    # Add a grid
    plt.grid()

    # Add legend
    plt.legend(fontsize=text_size, markerscale=0.75)

    # Set the limits of the axes
    plt.xlim(0, 130e3)
    plt.ylim(0, 2)
    plt.xticks([0,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000,110000,120000], 
            ["0", "10K", "20K", "30K", "40K", "50K", "60K", "70K", "80K", "90K", "100K", "110K", "120K"])

    plt.twinx()
    plt.ylabel('Average CPU Utilization (%)', fontsize=text_size)
    plt.yticks([x / (index+1) for x in range(0,201,25)])

    # Display the plot
    plt.savefig(plotname[index], bbox_inches='tight')
    plt.close()
    index += 1
