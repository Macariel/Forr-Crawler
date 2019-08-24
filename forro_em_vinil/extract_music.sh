#!/bin/bash -
# Go to directory of script
DIR="${0%/*}"
cd $DIR

ARCHIVES="$DIR/archives"
MUSIC_DIR=$(realpath "$DIR/../music/forro_em_vinil")

cd $MUSIC_DIR

# Delete empty directories
find . -maxdepth 1 -type d -empty -delete

# Extract archives
find $ARCHIVES -maxdepth 1 -type f -iname "*.rar" | while read archive; do
    unrar x "$ARCHIVES/$archive" \*.mp3 \.*MP3
    rm "$ARCHIVES/$archive"
done
