import os

# Directory where the files are located
directory = 'experiments/part2a/'

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        with open(os.path.join(directory, filename), 'r+') as file:
            lines = file.readlines()

            # Check if the last 3 lines are the appended averages
            if 'average user|average sys|average real' in lines[-2]:
                # Remove the last 3 lines
                file.seek(0)
                file.truncate()
                file.writelines(lines[:-3])