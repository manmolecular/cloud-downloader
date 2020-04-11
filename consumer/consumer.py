#!/usr/bin/env python3

import pika
from json import loads

from consumer.downloader import Downloader


class Consumer:
    def __init__(self):
        self.queue = "download_queue"
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)
        self.downloader = Downloader(base_path="data")

    def callback(self, ch, method, properties, body):
        url_list = loads(body)
        self.downloader.start_download(url_list=url_list, uuid=properties.correlation_id, processes=10)
        ch.basic_publish(exchange='',
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=str(properties.correlation_id))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback)
        self.channel.start_consuming()

    def __del__(self):
        self.connection.close()
