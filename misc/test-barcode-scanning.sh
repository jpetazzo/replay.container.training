#!/bin/sh
VIDEO_DEVICE=/dev/video8
SCREEN_WIDTH=1920
CROP_WIDTH=224
CROP_HEIGHT=72
CROP_X=$(($SCREEN_WIDTH-$CROP_WIDTH))
CROP_Y=0
ffmpeg -y -f v4l2 -i $VIDEO_DEVICE -vframes 1 -filter:v "crop=$CROP_WIDTH:$CROP_HEIGHT:$CROP_X:$CROP_Y" barcode.png
zbarimg barcode.png

