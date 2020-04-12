#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from os import environ

from database.config import Config

pg_connection = Config.DATABASE_URI


def choose_engine():
    pg_host = environ.get("POSTGRES_HOST") or "localhost"
    print(f"Use {pg_host} as Postgres host")
    try:
        override_pg_connection = pg_connection.replace("localhost", pg_host)
        engine = create_engine(override_pg_connection)
        if not database_exists(engine.url):
            create_database(engine.url)
        return engine
    except:
        pass


engine = choose_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
