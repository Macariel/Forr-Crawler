#!/usr/bin/env bash
if [[ "$#" -ne 2 ]];then
  echo "Expected two parameters. <youtube-url> <dest>"
  exit 1
fi

URL=$1
DEST="$2"

# Go to directory of script
SCRIPT_DIR="${0%/*}"
ROOT=$(realpath "$SCRIPT_DIR/..")
MUSIC_DIR="$ROOT/music/youtube"

cd $MUSIC_DIR
[[ ! -d $DEST ]] && mkdir $DEST
cd $DEST

youtube-dl -i -o "%(title)s.%(ext)s" -x --audio-format mp3 "$URL"
