#!/usr/bin/env python3

from consumer.consumer import Consumer
from sys import argv

if __name__ == "__main__":
    try:
        consumer = Consumer(host=argv[1])
    except:
        consumer = Consumer()
    consumer.start_consuming()
