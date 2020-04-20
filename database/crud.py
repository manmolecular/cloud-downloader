#!/usr/bin/env python3

from hashlib import sha512
from typing import AnyStr
from json import loads

from sqlalchemy.orm import Session

from database import models
from database import schemas
from database.database import SessionLocal, engine, Base


class DbManager:
    def __init__(self):
        pass

    def create_all(self):
        Base.metadata.create_all(engine)

    def create_user(self, user: schemas.User, session: Session = SessionLocal()):
        user_meta_as_dict = user.dict()
        user_meta_as_dict.update(
            {"password": sha512(user_meta_as_dict.get("password").encode()).hexdigest()}
        )
        user_model = models.User(**user_meta_as_dict)
        session.add(user_model)
        try:
            session.commit()
            session.refresh(user_model)
        except Exception:
            session.rollback()
        finally:
            session.close()

    def check_credentials(self, user: schemas.User, session: Session = SessionLocal()):
        user_meta_as_dict = user.dict()
        user_meta_as_dict.update(
            {"password": sha512(user_meta_as_dict.get("password").encode()).hexdigest()}
        )
        user_model = models.User(**user_meta_as_dict)
        user_db = (
            session.query(models.User)
            .filter(models.User.username == user_model.username)
            .first()
        )
        try:
            return user_db.password == user_model.password
        except:
            pass

    def create_task(self, task: schemas.Task, session: Session = SessionLocal()):
        task_model = models.Task(**task.dict())
        session.add(task_model)
        try:
            session.commit()
            session.refresh(task_model)
        except Exception:
            session.rollback()
        finally:
            session.close()

    def get_task_status(self, uuid: str, session: Session = SessionLocal()):
        try:
            return (
                session.query(models.Task).filter(models.Task.uuid == uuid).first().status
            )
        except:
            pass

    def get_task_urls(self, uuid: str, session: Session = SessionLocal()):
        try:
            return loads(session.query(models.Task).filter(models.Task.uuid == uuid).first().urls)
        except:
            pass

    def get_task_uuids(self, session: Session = SessionLocal()):
        return session.query(models.Task.uuid)

    def update_task_status(
        self, uuid: str, status: str, session: Session = SessionLocal()
    ):
        session.query(models.Task).filter_by(uuid=uuid).update({"status": status})
        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def get_user_id(self, username: AnyStr, session: Session = SessionLocal()):
        return (
            session.query(models.User)
            .filter(models.User.username == username)
            .first()
            .password
        )
