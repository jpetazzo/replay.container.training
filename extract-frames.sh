#!/bin/sh
set -eu

# This script extracts one frame every N seconds from the video file
# passed in argument. Then, it extracts the top-right section of the
# frame (where we expect to find a slide number), and runs tesseract
# (an OCR package) on that section. Finally, it writes one line of
# output per image, with the timestamp of the image and the detected
# text.

# You can adjust SECONDS_PER_FRAME. However if you want to do more
# than one frame per second, you will also have to adjust things
# further down.
#SECONDS_PER_FRAME=10
SECONDS_PER_FRAME=1
FRAMES_PER_SECOND=1/$SECONDS_PER_FRAME

TEMPDIR="$(mktemp -d)"

# Extract one frame every N seconds
# Grab the top-right 224x72 section
# (That's where we expect the slide number to be)
# Note, this assumes that the input is 1080p - or at least 1920px wide.
ffmpeg -i "$1" -filter:v "fps=fps=$FRAMES_PER_SECOND,crop=224:72:1696:0" "$TEMPDIR/out_%d.jpg"


N=0
while true; do
  N=$((N+1))
  BASE=$TEMPDIR/out_$N
  IMAGE=$BASE.jpg
  TEXT=$BASE.txt
  [ -f "$IMAGE" ] || break
  TIMESTAMP=$((($N-1)*$SECONDS_PER_FRAME))
  echo "Processing $IMAGE..." >/dev/stderr
  tesseract --dpi 300 --psm 7 "$IMAGE" "$BASE" >/dev/stderr
  printf "%s %s\n" "$TIMESTAMP" "$(head -n1 "$TEXT")"
  rm -f "$IMAGE" "$TEXT"
done

