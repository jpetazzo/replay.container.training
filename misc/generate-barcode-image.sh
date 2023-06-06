#!/bin/sh
# Note: when using CODE39, use only two letters or symbols.
# This should give a 228x72 pixels image, which is what we scan for.
zint --whitesp=3 --scale=2 --height 18  --barcode=CODE39 --notext --fg=CCCCCC --data=JP
