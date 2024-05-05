#!/bin/bash

for file in *.yaml; do
    for threads in 2 4 8; do
        new_file="${file%.yaml}-threads${threads}.yaml"
        sed "s/-n 1/-n $threads/" $file > $new_file
    done
done