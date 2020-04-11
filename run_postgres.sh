#!/usr/bin/env zsh

docker run --rm \
           --name cloud-down-postgres -p 127.0.0.1:5432:5432/tcp \
           -e POSTGRES_PASSWORD=pass1234 -e POSTGRES_USER=admin1234 \
           postgres:alpine
