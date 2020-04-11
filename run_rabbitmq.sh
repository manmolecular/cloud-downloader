#!/usr/bin/env zsh

docker run --rm \
           --name cloud-down-rabbitmq \
           -p 127.0.0.1:5672:5672/tcp \
           rabbitmq:alpine
