import os
import re
import numpy as np

# Directory where the files are located
directory = 'experiments/part2b/'

# Function to convert time format from minutes and seconds to seconds
def convert_to_seconds(time):
    print(time)
    minutes, seconds = map(float, time)
    print(minutes, seconds)
    return minutes * 60 + seconds

# Dictionary to store the baseline averages
baseline_averages = {}

# Then, calculate the averages and normalized values for each file
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        with open(os.path.join(directory, filename), 'r+') as file:
            lines = file.readlines()
            user_times = []
            sys_times = []
            real_times = []

            # Extract the user, sys and real times from each line
            for line in lines:
                time = re.findall("(\d+)m(\d+\.\d+)s", line)[0]

                if 'user' in line:
                    user_times.append(convert_to_seconds(time))
                elif 'sys' in line:
                    sys_times.append(convert_to_seconds(time))
                elif 'real' in line:
                    real_times.append(convert_to_seconds(time))

            # Calculate the average times
            avg_user = np.mean(user_times)
            avg_sys = np.mean(sys_times)
            avg_real = np.mean(real_times)


            # Append the average times and normalized values to the end of the file
            file.write(f'\naverage user|average sys|average real\n{avg_user}|{avg_sys}|{avg_real}\n')