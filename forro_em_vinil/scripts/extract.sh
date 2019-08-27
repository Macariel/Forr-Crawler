#!/bin/bash -
# Go to directory of script
DIR="${0%/*}"
cd $DIR

VINIL_ROOT=$(realpath "$DIR/..")
ARCHIVES="$VINIL_ROOT/archives"
MUSIC_DIR=$(realpath "$VINIL_ROOT/../music/forro_em_vinil/")

cd $MUSIC_DIR

# Delete empty directories
find . -maxdepth 1 -type d -empty -delete

echo Found $(find "$ARCHIVES/" -maxdepth 1 -type f -iname "*.rar" | wc -l ) archives

# Extract archives
find "$ARCHIVES/" -maxdepth 1 -type f -iname "*.rar" | while read archive; do
    echo Extracting $(basename "$archive")
    unrar x -y "$archive" \*.mp3 \*.wma \*.m4a \*.webm \*.ogg
    rm "$archive"
done
echo "Done"
