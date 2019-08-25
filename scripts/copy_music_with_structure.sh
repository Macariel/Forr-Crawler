#!/usr/bin/env bash
DIR="${0%/*}"
ROOT=$(realpath "$DIR/..")
MUSIC_DIR="$ROOT/music"

if [[ -z $1 ]]; then
    echo "Expected one parameter for the destination"
    exit 1
fi

find $MUSIC_DIR -type f -iregex ".*\.\(m4a\|mp3\|webm\)" -exec cp --parents {} "$1" \;
