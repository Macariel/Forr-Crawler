#!/bin/bash -
# Go to directory of script
DIR="${0%/*}"

VINIL_ROOT=$(realpath "$DIR/..")
ARCHIVES="$VINIL_ROOT/archives"
MUSIC_DIR=$(realpath "$VINIL_ROOT/../music/forro_em_vinil/")
PROCESSED="$VINIL_ROOT/progress-data"

cd $MUSIC_DIR
source $(realpath $VINIL_ROOT/../scripts)/formatting.sh

# Delete empty directories
find . -maxdepth 1 -type d -empty -delete

amount=$(find "$ARCHIVES/" -maxdepth 1 -type f -iname "*.rar" | wc -l )
echo Found $amount  archives

i=1
# Extract archives
find "$ARCHIVES/" -maxdepth 1 -type f -iname "*.rar" | while read archive; do
    green "$i/$amount "
    echo Extracting $(basename "$archive")
    unrar x -y "$archive" \*.mp3 \*.wma \*.m4a \*.webm \*.ogg \*.MP3 > /dev/null

    # Only delete archive if unrar was successful
    if [[ $? -eq 0 ]]; then
      echo $(basename "$archive") >> "$PROCESSED/processed_archives"
      rm "$archive"
    else
      red "[FAIL] " && echo "$archive"
    fi

    i=$((i+1))
done
echo "Done"
