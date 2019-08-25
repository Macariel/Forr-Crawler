#!/bin/bash - 
if [[ -z $1 ]];then
  echo "No argument given. Excepted exactly one"
  exit 0
fi

FILE_WITH_LINKS="$(realpath $1)"

# Go to directory of script
SCRIPT_DIR="${0%/*}"
cd $SCRIPT_DIR

# Progress data files
ROOT=$(realpath "$SCRIPT_DIR/..")
PROGRESS_DATA="$ROOT/progress-data"
FAILED="$PROGRESS_DATA/failed_links"
DEAD_LINKS="$PROGRESS_DATA/dead_links"
ALBUMS="$PROGRESS_DATA/downloaded_albums"
PROCESSED_LINKS="$PROGRESS_DATA/processed_links"

ARCHIVES=$(realpath "$ROOT/archives/")
MEGADOWN=$(realpath "$ROOT/bin/megadown")

> $FAILED 
find music/* -maxdepth 1 -type d -exec sh -c 'basename "$1" | iconv -f utf-8 -t ascii//TRANSLIT' _ {} \; > $ALBUMS

cd ARCHIVES
while read link; do
  # Check if link was already downloaded
  if [[ -z $(grep "$link" $PROCESSED_LINKS) ]]; then
    continue
  fi

  # Remove accents from characters (some archive names differ from the album names)
  album_name=$($MEGADOWN -qm $link | jq -r ".file_name" | cut -f 1 -d '.' | iconv -f utf-8 -t ascii//TRANSLIT)

  if [[ -z $album_name ]]; then
    echo "[FAIL] No album name found: \"$link\""
    echo $link >> $DEAD_LINKS
  elif [[ -z $(grep -r "$album_name" $ALBUMS) ]]; then
    $MEGADOWN -q $link

    if [[ $? -eq 0 ]]; then
      echo "[NEW] \"$album_name\""
    else
      echo "[FAIL] Cannot download: \"$link\""
      echo $link >> $FAILED
    fi
  else
    echo $link >> processed_links
    echo "Skipping \"$album_name\" (exists already)"
  fi
done < "$FILE_WITH_LINKS"
