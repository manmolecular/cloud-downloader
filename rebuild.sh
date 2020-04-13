#!/usr/bin/env sh

docker-compose up --scale cloud-downloader-consumer=5 --build --remove-orphans
