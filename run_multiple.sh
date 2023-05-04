#!/bin/bash

output_file="output.txt"
time_output_file="times.txt"
rm -f "$output_file" # Remove the output file if it exists
rm -f "$time_output_file" # Remove the time output file if it exists

for i in {1..1000}
do
  (time (python3.10 -m referee minimax_test minimax_test | tail -n 25 >> "$output_file")) 2>&1 | grep real | sed 's/real//' | sed 's/^[ \t]*//' >> "$time_output_file"
done
