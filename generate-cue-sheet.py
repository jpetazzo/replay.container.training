#!/usr/bin/env python

import os
import sys

toc_file = sys.argv[1]
ocr_files = sys.argv[2:]

toc = []
for line in open(toc_file):
  line = line.strip()
  slide_number, section_size, section_title = line.split("\t")
  if slide_number == "0":
    continue
  if slide_number == "index":
    continue
  toc.append((int(slide_number), section_title))

# Build an array containing the text that has been extracted
# from the frames of all our video files.
ocrs = []
for ocr_file in ocr_files:
  video_file = os.path.join("rec", os.path.basename(ocr_file)[:-4])
  for line in open(ocr_file):
    timestamp, text = line.split(" ", 1)
    if "/" in text:
      slide_number = text.split("/")[0]
      if slide_number.isdigit():
        ocrs.append((video_file, timestamp, slide_number))

# Now, given the table of contents (toc) that maps each
# section to the number of its title slide, find the first
# time that this title slide shows up in our video files.
# The title slide might not be found; so we'll also look for
# the slides around it.
# The output will be a list of tuples (video_file, timestamp, title).
# For sections that aren't found, add a dummy entry.
titles = []
for slide_number, section_title in toc:
  for offset in [0, 1, 2, 3, 4, 5, -1, -2, -3, -4, -5]:
    looking_for = str(slide_number + offset)
    frames = [ ocr for ocr in ocrs if ocr[-1] == looking_for ]
    if frames:
      file_name, timestamp, _ = frames[0]
      break
  else:
    file_name, timestamp = "#", "0"
  titles.append((file_name, float(timestamp), section_title))

def convert_timestamp(ts):
  hms, ms = ts.strip().split(",")
  h, m, s = hms.split(":")
  h, m, s, ms = map(int, (h, m, s, ms))
  return h*3600 + m*60 +s + 0.001*ms

# Read all the subtitles, and put them in a list of tuples
# with (video_file, timestamp1, timestamp2, text).
# The goal of this is to be able to sort together the
# "titles" and "subtitles" lists.
subtitles = []
for ocr_file in ocr_files:
  base = os.path.basename(ocr_file)[:-4]
  video_file = os.path.join("rec", base)
  srt_file = os.path.join("asr", base + ".srt")
  lines = open(srt_file).readlines()
  while lines:
    index, timestamps, text, blank = lines[:4]
    lines = lines[4:]
    t1, t2 = timestamps.split(" --> ")
    t1, t2 = map(convert_timestamp, (t1, t2))
    text = text.strip()
    subtitles.append((video_file, t1, str(t2), text))

# Finally, generate the final cue sheet.
file_name = None
for entry in sorted(titles + subtitles):
  if entry[0] == "#":
    print(f"#TITLE\t{entry[-1]}")
    continue
  if entry[0] != file_name:
    file_name = entry[0]
    print(f"SOURCE\t{file_name}")
  if len(entry) == 3:
    print(f"TITLE\t{entry[-1]}")
  if len(entry) == 4:
    print(f"TEXT\t{entry[1]}\t{entry[2]}\t{entry[3]}")

