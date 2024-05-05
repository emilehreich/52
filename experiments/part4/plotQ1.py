import pandas as pd
import matplotlib.pyplot as plt
import glob

# Get a list of all txt files in the current directory
files = glob.glob('memcachedT?C?.txt')
# files.append('memcachedT16C1.txt')
# files.append('memcachedT16C2.txt')

# create a new figure
plt.figure(figsize=(15, 9))

# Define column headers
headers = ['type', 'avg', 'std', 'min', 'p5', 'p10', 'p50', 'p67', 'p75', 'p80', 'p85', 'p90', 'p95', 'p99', 'p999', 'p9999', 'QPS', 'target', 'ts_start', 'ts_end'] 

# Okabe-Ito color palette                 
#           black     orange     skyblue  bluishgreen red-purple    gray
colors = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#CC79A7", "#999999"] 
markers = ["v", "s", "^", "o", "o", "o"]

# Loop through the files list and plot the data from each file
for index, file in enumerate(files):
    # Load data from file into a pandas DataFrame
    print(file)
    df = pd.read_csv(file, delim_whitespace=True, comment='#', names=headers)

    # Convert p95 from microseconds to milliseconds
    df['p95'] = df['p95'] / 1e3

    # Group the DataFrame by 'QPS' and compute the mean of 'p95'
    grouped = df.groupby('target')[['QPS', 'p95']]
    result_mean = grouped.mean()
    result_error = grouped.sem()

    # Plot QPS vs average p95, with error bars for stddev (QPS and p95)
    plt.errorbar(result_mean['QPS'], result_mean['p95'], xerr=result_error['QPS'], yerr=result_error['p95'], capsize=2,
                 label=file[9:-4], linestyle='--', linewidth=1.0, color=colors[index+1], marker=markers[index], markersize=10, fillstyle='none')

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

# Title for the plots
# plt.title('Latency vs QPS over various interference types', fontsize=text_size)

# Display the plot
plt.savefig("part4_q1.pdf", bbox_inches='tight')
