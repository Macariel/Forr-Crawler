#!/usr/bin/env bash
if [[ "$#" -ne 1 ]];then
  echo "Expected one parameter: <soundcloud-url>"
  exit 1
fi

# Go to directory of script
SCRIPT_DIR="${0%/*}"
ROOT=$(realpath "$SCRIPT_DIR/..")
MUSIC_DIR="$ROOT/music/soundcloud"

cd $MUSIC_DIR

scdl --extract-artist --addtofile -l $1