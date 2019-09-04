#!/usr/bin/env bash
DIR="${0%/*}"
find $(realpath $DIR/../music) -type f -iregex ".*\(\.mp3\|\.webm\|\.m4a\)" > all_titles.txt
