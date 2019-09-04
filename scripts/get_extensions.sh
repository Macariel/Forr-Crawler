#!/usr/bin/env bash
DIR="${0%/*}"
find $(realpath $DIR/../music/) -type f | sed 's!.*/!!' | awk -F . '{ print $NF }' | sort | uniq -c | sort -gr
