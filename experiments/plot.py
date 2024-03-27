import pandas as pd
import matplotlib.pyplot as plt
import glob

# Get a list of all txt files in the current directory
files = glob.glob('*.txt')

# create a new figure
plt.figure(figsize=(12, 9))

# Define column headers
headers = ['type', 'avg', 'std', 'min', 'p5', 'p10', 'p50', 'p67', 'p75', 'p80', 'p85', 'p90', 'p95', 'p99', 'p999', 'p9999', 'QPS', 'target']

# Loop through the files list and plot the data from each file
for file in files:
    # Load data from file into a pandas DataFrame
    df = pd.read_csv(file, delim_whitespace=True, comment='#', names=headers)

    # Convert p95 from microseconds to milliseconds
    df['p95'] = df['p95'] / 1e3

    # Group the DataFrame by 'QPS' and compute the mean of 'p95'
    grouped = df.groupby('target')[['QPS', 'p95']]
    result_mean = grouped.mean()
    result_error = grouped.sem()

    # Plot QPS vs average p95, with error bars for stddev (QPS and p95)
    plt.errorbar(result_mean['QPS'], result_mean['p95'], xerr=result_error['QPS'], yerr=result_error['p95'], label=file, linewidth=0.01)

# Set the size of the text
text_size = 16.5

# labeling axes
plt.xlabel('QPS', fontsize=text_size)
plt.ylabel('Average p95 (ms)', fontsize=text_size)

# Add legend
plt.legend(fontsize=text_size)

# Title for the plots
plt.title('Average QPS vs p95 (ms)', fontsize=text_size)

# Display the plot
plt.savefig("exp.pdf")
