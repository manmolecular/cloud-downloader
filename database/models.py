#!/usr/bin/env python3

from sqlalchemy import Column, Integer, String

from database.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', password='{self.password}')>"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    status = Column(String)

    def __repr__(self):
        return (
            f"<Task(id='{self.id}', uuid='{self.username}', status='{self.password}')>"
        )
