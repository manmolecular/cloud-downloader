#!/usr/bin/env python3

import pika
from json import dumps
from uuid import uuid4
from database.crud import DbManager

manager = DbManager()


class Publisher:
    def __init__(self):
        self.queue = "download_queue"
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        manager.update_task_status(uuid=props.correlation_id, status="done")
        print(f"Done task {props.correlation_id}")

    def publish_task(self, task: list):
        corr_id = str(uuid4())
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=corr_id,
            ),
            body=dumps(task)
        )
        return corr_id

    def process_data_events(self):
        self.connection.process_data_events(time_limit=1)

    def __del__(self):
        self.connection.close()
