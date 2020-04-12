FROM python:3.8-alpine as cloud-downloader-consumer

LABEL org.label-schema.name="Cloud Downloader Consumer" \
      org.label-schema.description="RabbitMQ Consumer/Downloader" \
      org.label-schema.license="GPL-2.0"

COPY consumer /app/consumer/
COPY consumer.py /app/consumer.py
WORKDIR /app
RUN pip install --no-cache-dir requests pika

ENV PYTHONPATH="/app"
ENTRYPOINT ["python3", "consumer.py"]
