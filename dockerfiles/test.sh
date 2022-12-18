#!/bin/sh
set -eu
for DOCKERFILE in ${1-Dockerfile.*}; do
  TAG="${DOCKERFILE#Dockerfile.}"
  docker build . -t "whisper:$TAG" -f "Dockerfile.$TAG"
  docker images "whisper:$TAG"
  #docker run -t -v "$PWD/../cache:/root/.cache" -v "$PWD/data:/data" -w /data "whisper:$TAG" whisper test.m4a
done
docker images whisper



