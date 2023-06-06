# replay.container.training aka ChatJpetazzo

Legend:
- 📚️ Course materials
- 📽️ Recorded course
- 🤖 Generated files
- 📝 Manual text editing

```
data
└── 2023-01-m1
    ├── rec
    │   ├── 📽️ part1.mp4
    │   └── 📽️ part2.mp4
    ├── ocr
    │   ├── 🤖 part1.mp4.ocr
    │   └── 🤖 part2.mp4.ocr
    ├── asr
    │   ├── 🤖 part1.mp4.srt
    │   └── 🤖 part2.mp4.srt
    ├── 📚️ slides.yml
    ├── 📚️ slides.yml.html
    ├── 🤖 toc.tsv
    ├── 🤖 generatedcue.tsv
    ├── 📝 editedcue.tsv
    └── cut
        ├── 🤖 001 - Introduction.mp4
        ├── 🤖 001 - Introduction.mp4.srt
        ├── 🤖 002 - Getting Started.mp4
        ├── 🤖 002 - Getting Started.mp4.srt
        ├── 🤖 ...
        ├── 🤖 042 - Final Words and Next Steps.mp4
        ├── 🤖 042 - Final Words and Next Steps.mp4.srt
        └── 🤖 index.html
```

## Generate initial audio transcripts

- input: `rec/*.mp4`
- output: `asr/*.mp4.srt`
- command: `docker-compose up whisper FIXME`
- remarks: uses whisper; faster with GPU

## Detect slides numbers in recorded media

- input: `rec/*.mp4`
- output: `ocr/*.mp4.ocr`
- command: `docker-compose up tesseract FIXME`
- remarks: uses ffmpeg to extract frames, and tesseract to run OCR on them

## Generate TOC file

- input: `slides.yml` + `slides.yml.html`
- output: `toc.tsv`
- command: `count-slides.py` from `container.training` repo

## Generate cue sheet

- input: `toc.tsv` + `ocr/*.ocr`
- output: `generatedcue.tsv`
- command: `generate-cue-sheet.py toc.tsv part1.mp4.ocr part2.mp4.ocr`

## Edit cue sheet

- input: `generatedcue.tsv`
- output: `editedcue.tsv`
- command: do this manually with your fav text editor

## Cut video chapters

- input: `generatedcue.tsv` + `rec/*.mp4`
- output: `cut/*.mp4`
- command: `process-cue-sheet.py cue.tsv`

## Generate final subtitles

- input: `cut/*.mp4`
- output: `cut/*.mp4.srt`
- command: FIXME

## Generate HTML page

- input: `cut/*.mp4` + `cut/*.mp4.srt`
- output `cut/index.html`

## TODO

- transform big mp4 files into some kind of HLS/adaptive stream
- automate uploads
- leverage silence detection to add them to cue sheet
- leverage silence detection to add breaks in rendered paragraphs
