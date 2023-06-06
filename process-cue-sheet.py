#!/usr/bin/env python

import hashlib
import os
import subprocess
import sys

cue_sheet_file = sys.argv[1]

cue_sheet = []
source_file = None
title = "(No title set; please add a TITLE line!)"
sections = {}
sections_list = []
for line in open(cue_sheet_file):
  if line.startswith("#"):
    continue
  command, *args = line.strip().split("\t")
  if command == "SOURCE":
    source_file = args[0]
  elif command == "TITLE":
    title = args[0]
    if title not in sections:
      sections[title] = []
      sections_list.append(title)
  elif command == "TEXT":
    section = sections[title]
    ts1, ts2, text = args
    ts1, ts2 = map(float, (ts1, ts2))
    # If this is the first entry in the section, it's super easy: just add it!
    if not section:
      section.append([source_file, ts1, ts2, [text]])
    else:
      # Otherwise, check if we extend the current span, or create a new one.
      if section[-1][0] == source_file and abs(section[-1][2] - ts1) < 0.5:
        # If it's the same source file, and the previous section ends a very
        # short time within the start of the new section, then extend the current
        # span.
        section[-1][2] = ts2
        section[-1][3].append(text)
      else:
        # Otherwise, create a new span.
        section.append([source_file, ts1, ts2, [text]])

CACHE_DIR = os.getenv("CACHE_DIR", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def hash_string(s):
  if type(s) == str:
    s = s.encode("utf-8")
  return hashlib.sha256(s).hexdigest()

def hash_file(filename):
  stat = os.stat(filename)
  first_16_megs = open(filename, "rb").read(16000000)
  return hash_string(str((stat.st_size, stat.st_mtime, hash_string(first_16_megs))))

def cached_exec(command, input_files, output_file):
  assert not os.path.exists(output_file)
  command_hash = hash_string(str(command))
  input_hashes = [ hash_file(f) for f in input_files ]
  exec_hash = hash_string(str((command_hash, input_hashes)))
  cache_file = os.path.join(CACHE_DIR, exec_hash)
  if os.path.exists(cache_file):
    subprocess.check_call(["cp", cache_file, output_file])
  else:
    subprocess.check_call(command)
    subprocess.check_call(["cp", output_file, cache_file])

def unfloat(f):
  return "{:.3f}".format(f)

# OK, at this point, we have an ordered list of sections;
# and for each section, we have a list of spans indicating
# the media segments to assemble together.
# Let's display that.
for section_index, title in enumerate(sections_list):
  print(f"{section_index+1:03} - {title}")
  section = sections[title]
  chunks = []
  for chunk_index, (source_file, ts1, ts2, texts) in enumerate(section):
    output_file = f"{section_index+1:03}_{chunk_index}.mp4"
    print(source_file, ts1, ts2)
    ffmpeg = [
      "ffmpeg", "-hide_banner", "-nostdin",
      #"-vsync", "0", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-extra_hw_frames", "8", #NVIDIA
      "-ss", unfloat(ts1), "-i", source_file, "-t", unfloat(ts2-ts1),
      "-c:a", "copy",
      "-c:v", "libx264", "-preset", "ultrafast",  #CPU
      #"-c:v", "h264_nvenc",  #NVIDIA
      output_file
    ]
    cached_exec(ffmpeg, [source_file], output_file)
    chunks.append(output_file)
  with open("concat.txt", "w") as f:
    for chunk in chunks:
      f.write(f"file '{chunk}'\n")
  output_file = f"{OUTPUT_DIR}/{section_index+1:03} - {title}.mp4"
  ffmpeg = [
    "ffmpeg", "-hide_banner", "-nostdin",
    "-f", "concat", "-i", "concat.txt",
    "-c", "copy",
    output_file
  ]
  cached_exec(ffmpeg, chunks, output_file)
  os.unlink("concat.txt")
  for chunk in chunks:
    os.unlink(chunk)

