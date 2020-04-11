#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from database.config import Config

pg_connection = Config.DATABASE_URI


def choose_engine():
    for network in ["localhost", "postgres", "docker.host.internal", "docker.for.mac.host.internal", "host.docker.internal"]:
        if network == "localhost":
            continue
        try:
            print(f"Use {network} as db host")
            override_pg_connection = pg_connection.replace("localhost", network)
            engine = create_engine(override_pg_connection)
            if not database_exists(engine.url):
                create_database(engine.url)
            return engine
        except:
            pass


engine = choose_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
