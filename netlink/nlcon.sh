#!/bin/bash

rm route4.*.txt

echo "Recording known good configuration..."
ip -4 route > route4.old.txt

for((i=0; ;++i)); do
    ip -4 route > route4.new.txt
    if diff route4.old.txt route4.new.txt > route4.diff.txt; then
        echo "Pass $i"
    else
        echo "Fail $i"
        exit 1
    fi

    sleep 5
done