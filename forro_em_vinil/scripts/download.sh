#!/bin/bash -

if [[ -z $1 ]];then
  echo "No argument given. Expected exactly one"
  exit 1
fi

FILE_WITH_LINKS="$(realpath $1)"

# Go to directory of script
SCRIPT_DIR="${0%/*}"

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
echo "# Fetching already downloaded album names"
find $(realpath "$ROOT/../music/forro_em_vinil/*") -maxdepth 1 -type d -exec sh -c 'basename "$1" | iconv -f utf-8 -t ascii//TRANSLIT' _ {} \; > $ALBUMS

if [[ ! -f $PROCESSED_LINKS ]]; then
    touch $PROCESSED_LINKS
fi

cd $ARCHIVES
while read link; do
  # Check if link was already downloaded
  if [[ ! -z $(grep "$link" $PROCESSED_LINKS) ]]; then
    echo "[DONE] Already downloaded: $link"
    continue
  fi

  # Check if the link is still up
  metadata="$($MEGADOWN -qm $link 2>&1)"
  if [[ -n $(echo "$metadata" | grep "MEGA ERROR") ]]; then
    echo "[FAIL] Link dead: $link"
    echo "$link" >> $DEAD_LINKS
    continue
  fi

  # Remove accents from characters (some archive names differ from the album names)
  album_name=$($MEGADOWN -qm $link | jq -r ".file_name" | cut -f 1 -d '.' | iconv -f utf-8 -t ascii//TRANSLIT)

  if [[ -z $album_name ]]; then
    echo "[FAIL] No album name found: $link"
    echo $link >> $DEAD_LINKS
  elif [[ -z $(grep -r "$album_name" $ALBUMS) ]]; then
    output=$($MEGADOWN -q $link 2>&1)

    if [[ $? -eq 0 ]]; then
      echo "[NEW] $album_name"
      echo $link >> $PROCESSED_LINKS
    else
      echo "[FAIL] Temporary unavailable ($( echo $output | tr -d '\n')): $link"
      echo $link >> $FAILED
    fi
  else
    echo $link >> $PROCESSED_LINKS
    echo "Skipping \"$album_name\" (exists already)"
  fi
done < "$FILE_WITH_LINKS"

# Remove multiple value
sort -u -o $DEAD_LINKS $DEAD_LINKS
sort -u -o $FAILED $FAILED
