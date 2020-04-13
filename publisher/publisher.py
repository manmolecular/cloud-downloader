#!/usr/bin/env python3

from json import dumps

import pika

from database.crud import DbManager

manager = DbManager()


class Publisher:
    def __init__(self, host: str = "localhost"):
        self.queue = "download_queue"
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

    def on_response(self, ch, method, props, body):
        manager.update_task_status(uuid=props.correlation_id, status="done")
        print(f"Done task {props.correlation_id}")

    def publish_task(self, task: list, uuid: str):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue, correlation_id=uuid,
            ),
            body=dumps(task),
        )

    def process_data_events(self):
        self.connection.process_data_events(time_limit=1)

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass
