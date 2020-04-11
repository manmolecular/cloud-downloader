#!/usr/bin/env python3
from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., min_length=1, max_length=10)
    password: str = Field(..., min_length=1, max_length=100)


class Task(BaseModel):
    uuid: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., min_length=1, max_length=100)

