#!/usr/bin/env python3

from consumer.consumer import Consumer
from os import environ

if __name__ == "__main__":
    try:
        rabbit_mq_host = environ.get("RABBITMQ_HOST") or "localhost"
        print(f"Use {rabbit_mq_host} as RabbitMQ host")
        consumer = Consumer(host=rabbit_mq_host)
    except:
        consumer = Consumer()
    consumer.start_consuming()
