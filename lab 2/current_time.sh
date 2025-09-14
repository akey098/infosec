#!/bin/bash
set -euo pipefail

current_time=$(date +%H:%M)
current_hour=$(date +%H)
current_minute=$(date +%M)
workday_end=18

echo "Time is $current_time"

if ((current_hour >= workday_end)); then
	echo "Work is over for today"
else
	hours_left=$((workday_end - current_hour - 1))
	minutes_left=$((60 - current_minute))
echo "There is still $hours_left hours and $minutes_left minutes left"
fi