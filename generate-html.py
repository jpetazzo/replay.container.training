#!/usr/bin/env python

import sys, yaml

lang = sys.argv.pop(1)
assert lang in ["en", "fr"]
video_files = sys.argv[1:]

translations = yaml.safe_load("""
select chapter:
  en: Select a training chapter
  fr: Sélectionnez un chapitre de la formation
click in text for direct access:
  en: |
    You can directly access a specific part of the video
    by clicking in the transcript below.
  fr: |
    Vous pouvez accéder directement à la partie de la vidéo qui
    vous intéresse en cliquant dans le texte ci-dessous.
""")

# TODO
def _(s, lang=lang):
  return translations[s][lang]

print("""<!doctype html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<style>

body {
  font-family: sans;
}

div.videopanel {
  position: fixed;
  left: 0;
  top: 0;
  background: lightgrey;
}

div.pickerpanel {
  position: fixed;
  background: lightgrey;
  left: 0;
  padding-left: 8px;
  width: 100%;
}

/* if the display is high enough:
  - scale the video to full width
  - put the text below
 */
@media (max-aspect-ratio: 3/2) {
  div.videopanel {
    width: 100%;
    height: calc(100vw / 1920 * 1080);
  }

  video {
    width: 100%;
    height: 100%;
  }

  div.pickerpanel {
    top: calc(100vw / 1920 * 1080);
    height: 3em;
  }

  div.textpanel {
    top: calc(100vw / 1920 * 1080 + 3em);
  }
}

/* if the display is wide enough:
  - scale video to take up the whole height
  - put the text on the right
 */
@media (min-aspect-ratio: 5/2) {
  div.videopanel {
    height: 100%;
    width: calc(100vh / 1080 * 1920);
  }

  video {
    height: 100%;
    width: calc(100vh / 1080 * 1920);
  }

  div.pickerpanel {
    top: 0;
    height: 3em;
    margin-left: calc(100vh / 1080 * 1920);
  }

  div.textpanel {
    left: calc(100vh / 1080 * 1920 + 8px);
    top: 3em;
  }
}

/* otherwise:
   - scale the video to take a fraction of the height
   - put the text below
 */
@media (min-aspect-ratio: 3/2) and (max-aspect-ratio: 5/2) {
  div.videopanel {
    height: 60vh;
    width: 100%;
  }

  video {
    height: 100%;
    width: calc(60vh / 1080 * 1920);
  }

  div.pickerpanel {
    top: 60vh;
    height: 3em;
  }

  div.textpanel {
    top: calc(60vh + 3em);
  }
}

div.textpanel {
  position: absolute;
  z-index: -1;
}

div.text {
  display: none;
}

div.text.current {
  display: initial;
}

#video_picker {
  margin-top: 8px;
}

.text a {
  text-decoration: none;
  color: black;
  font-style: italic;
}

.text a:hover {
  text-decoration: underline;
}

</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js"></script>
<script>

function play(src, time) {
  let video = document.querySelector("video");
  video.src = src;
  video.currentTime = time;
  video.play();
}

function pick_video() {
  let picker = document.querySelector("#video_picker");
  let video_id = picker.value;
  let video_div = document.querySelector("#" + video_id);
  document.querySelectorAll(".current").forEach(
    x => x.classList.remove("current")
  ); 
  video_div.classList.add("current");
  document.querySelector(".current a").click();
}

</script>
</head>
"""
+
f"""
<body onload="javascript:pick_video();">
  <div class="warning" style="position: absolute; z-index: 9;background: yellow;font-weight: bold;">⚠️ Beta version, use at your own risk😎</div>
  <div class="videopanel">
    <video controls></video>
  </div>
  <div class="pickerpanel">
    <label for="video_picker">{_("select chapter")} → </label>
    <select id="video_picker" onChange="javascript:pick_video();">
""")

for video_index, video_file in enumerate(video_files):
  print(f"""
        <option value="video_{video_index}">{video_file}</option>
""")
print("""
    </select>
  </div>
  <div class="textpanel">
""")

for video_index, video_file in enumerate(video_files):
  quoted_video_file = video_file.replace("'",r"\'").replace('"', '&quot;')
  print(f"""
<div class="text" id="video_{video_index}">
<p>
{_("click in text for direct access")}
</p>
<p>
""")
  srt_file = video_file + ".srt"
  lines = open(srt_file).readlines()
  while lines:
    line_number, timestamps, text, blank = lines[:4]
    lines = lines[4:]
    h, m, s = map(int, timestamps.split(",")[0].split(":"))
    ts = 3600*h + 60*m + s
    print(f"""
<a href="javascript:play('{quoted_video_file}', {ts})">{text}</a>
""")
  print("</p></div>")

print("</div></body></html>")
