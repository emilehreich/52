#!/bin/bash

# Function to get the number of incomplete jobs
get_incomplete_jobs_count() {
  kubectl get jobs | awk '/parsec-*/{print $2}'
}

# Main loop
while true; do
  # Get the number of incomplete jobs
  incomplete_jobs=$(get_incomplete_jobs_count)
  
  echo "Checking... there are ${incomplete_jobs} complete jobs."

  # Break the loop if all jobs are complete
  if [[ "${incomplete_jobs}" -eq "1/1" ]]; then
    echo "All jobs have completed."
    break
  fi
  
  # Wait for 5 seconds before checking again
  sleep 5
done
