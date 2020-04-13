#!/usr/bin/env python3

from consumer.consumer import Consumer
from os import environ

RABBIT_MQ_HOST = environ.get("RABBITMQ_HOST") or "localhost"
print(f"Use {RABBIT_MQ_HOST} as RabbitMQ host")


if __name__ == "__main__":
    try:
        consumer = Consumer(host=RABBIT_MQ_HOST)
        consumer.start_consuming()
        print(f"Connected to RabbitMQ")
    except:
        print(
            "RabbitMQ currently unavailable, {action}".format(
                action="exit" if RABBIT_MQ_HOST == "localhost" else "trying to reconnect..."
            )
        )
