#!/bin/bash -
if [[ -z $1 ]];then
  echo "No argument given. Expected exactly one"
  exit 1
fi

FILE_WITH_LINKS="$(realpath $1)"

# Directory of script
SCRIPT_DIR="${0%/*}"

# Progress data files
ROOT=$(realpath "$SCRIPT_DIR/..")
PROGRESS_DATA="$ROOT/progress-data"
PROCESSED_LINKS="$PROGRESS_DATA/processed_links"
PROCESSED_ARCHIVES="$PROGRESS_DATA/processed_archives"
ALBUMS="$PROGRESS_DATA/downloaded_albums"

ARCHIVES=$(realpath "$ROOT/archives/")
MEGADOWN=$(realpath "$ROOT/bin/megadown")

# include formatting functions
source $(realpath $ROOT/../scripts)/formatting.sh

underlined "# Fetching already downloaded album names\n"
find $(realpath "$ROOT/../music/forro_em_vinil/") -maxdepth 1 -type d -exec sh -c 'basename "$1" | iconv -f utf-8 -t ascii//TRANSLIT' _ {} \; > $ALBUMS

if [[ ! -f $PROCESSED_LINKS ]]; then
    touch $PROCESSED_LINKS
fi

cd $ARCHIVES
i=1
max=$(wc -l < $FILE_WITH_LINKS)
while read link; do
  # Counter
  green "$i/$max "
  i=$((i+1))

  # Check if link was already downloaded
  if [[ -n $(grep "$link" $PROCESSED_LINKS) ]]; then
    echo "[DONE] Already downloaded: $link"
    continue
  fi

  # Check if the link is still up
  metadata="$($MEGADOWN -qm $link 2>&1)"
  if [[ -n $(echo "$metadata" | grep "MEGA ERROR") ]]; then
    red "[FAIL]"; echo " Link dead: $link"
    continue
  fi

  # Get filename from mega download
  filename=$($MEGADOWN -qm $link | jq -r ".file_name")
  extension="${filename##*.}"
  basename="${filename%.*}"
  
  # Check that the file is an archive
  if [[ "$extension" != "rar" ]]; then
    echo "[DONE] Not an archive: $filename ($link)"
    continue
  fi

  # Check if file already exists
  if [[ -f "$filename" ]] || [[ -n $(grep "$filename" $PROCESSED_ARCHIVES ) ]]; then
    echo "[DONE] File already exists"
    continue
  fi

  # Remove accents from characters (some archive names differ from the album names)
  album_name=$(echo "$basename" | iconv -f utf-8 -t ascii//TRANSLIT)

  if [[ -z $album_name ]]; then
    red "[FAIL]"; echo " No album name found: $link"
  elif [[ -z $(grep -r "$album_name" $ALBUMS) ]]; then
    blue "[NEW]"; echo " Downloading $album_name"
    output=$($MEGADOWN $link)

    if [[ $? -eq 0 ]]; then
      echo $link >> $PROCESSED_LINKS
    else
      red "[FAIL]"; echo " Temporary unavailable ($( echo $output | tr -d '\n')): $link"
    fi
  else
    echo $link >> $PROCESSED_LINKS
    echo "Skipping \"$album_name\" (exists already)"
  fi
done < "$FILE_WITH_LINKS"
