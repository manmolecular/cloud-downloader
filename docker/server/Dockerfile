FROM python:3.8-alpine as cloud-downloader-server

LABEL org.label-schema.name="Cloud Downloader Server" \
      org.label-schema.description="Cloud Downloader Server" \
      org.label-schema.license="GPL-2.0"

COPY consumer /app/consumer/
COPY database /app/database/
COPY publisher /app/publisher/
COPY server.py /app/server.py
COPY settings.py /app/settings.py
COPY requirements.txt /app/requirements.txt

WORKDIR /app
RUN apk add --no-cache postgresql-dev gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8888
ENV PYTHONPATH="/app"
ENTRYPOINT ["python3", "server.py"]
