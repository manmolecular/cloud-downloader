#!/usr/bin/env python3


class Config:
    DATABASE_URI = "postgres+psycopg2://admin1234:pass1234@localhost:5432/cloud"
    LOCAL_NETWORKS = [
        "localhost",
        "cloud-downloader-db",
        "postgres",
        "docker.host.internal",
        "docker.for.mac.host.internal",
        "host.docker.internal",
    ]
