#!/bin/bash

# Function to get the number of incomplete jobs
get_complete_jobs() {
  kubectl get jobs | awk '/parsec-*/{split($2,a,"/"); print a[1]}'
}

# Main loop
while true; do
  # Get the number of incomplete jobs
  complete=$(get_complete_jobs)
  
  echo "Checking... there are ${complete} complete jobs."

  # Break the loop if all jobs are complete
  if [[ "${complete}" -eq "1" ]]; then
    echo "All jobs have completed."
    break
  fi
  
  # Wait for 5 seconds before checking again
  sleep 5
done
