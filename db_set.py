#!/usr/bin/env python3

from database.crud import DbManager
from database.schemas import User

if __name__ == "__main__":
    manager = DbManager()
    manager.create_all()
    user_schema = User(**{"username": "user1", "password": "pass1"})
    manager.create_user(user_schema)
    print(manager.get_user_id(username="user1"))
