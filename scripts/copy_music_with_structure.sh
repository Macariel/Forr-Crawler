#!/usr/bin/env bash
find . -type f -iregex ".*\.\(m4a\|mp3\|webm\)" -exec cp --parents {} /media/pawelka/Forro/ \;
