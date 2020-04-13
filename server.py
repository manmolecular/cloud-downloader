import json

import tornado.escape
import tornado.ioloop
import tornado.process
import tornado.web
from os import environ
from uuid import uuid4
from sys import exit

import settings
from database.crud import DbManager
from database.schemas import User, Task
from publisher.publisher import Publisher

RABBIT_MQ_HOST = environ.get("RABBITMQ_HOST") or "localhost"
print(f"Use {RABBIT_MQ_HOST} as RabbitMQ host")

try:
    PUBLISHER = Publisher(host=RABBIT_MQ_HOST)
    print(f"Connected to RabbitMQ")
except:
    print(
        "RabbitMQ currently unavailable, {action}".format(
            action="exit" if RABBIT_MQ_HOST == "localhost" else "trying to reconnect..."
        )
    )
    exit(1)
try:
    DB_MANAGER = DbManager()
    print(f"Connected to Postgres")
except:
    print(
        "Postgres currently unavailable, {action}".format(
            action="exit" if RABBIT_MQ_HOST == "localhost" else "trying to reconnect..."
        )
    )
    exit(1)


class GetStatusHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        if self.get_secure_cookie("user"):
            uuid = self.get_argument("uuid", None)
            self.write(
                {
                    "status": "ok",
                    "info": DB_MANAGER.get_task_status(uuid) or "Not exists",
                    "uuid": uuid,
                }
            )
        else:
            self.write({"status": "fail", "info": "User not logged in"})


class UploadUrlsHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        self.write({"status": "ok", "info": "Upload list of URLs with POST method into the cloud"})

    def post(self):
        if self.get_secure_cookie("user"):
            url_list = json.loads(self.request.body)
            uuid = str(uuid4())
            PUBLISHER.publish_task(url_list, uuid)
            task_schema = Task(**{"uuid": uuid, "status": "in progress"})
            DB_MANAGER.create_task(task_schema)
            self.write({"status": "ok", "info": "Task created", "uuid": uuid})
        else:
            self.write({"status": "fail", "info": "User not logged in"})


class RegisterHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def post(self):
        user_schema = User(**json.loads(self.request.body))
        DB_MANAGER.create_user(user_schema)
        self.write({"status": "ok", "info": "User registered"})


class AuthLoginHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def check_permission(self, user_schema):
        return DB_MANAGER.check_credentials(user_schema)

    def post(self):
        user_schema = User(**json.loads(self.request.body))
        username = user_schema.username
        auth = DB_MANAGER.check_credentials(user_schema)
        if auth:
            self.set_current_user(username)
            self.write({"status": "ok", "info": "User logged in"})
        else:
            self.write({"status": "fail", "info": "Invalid credentials"})
            pass

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", "123")
        else:
            self.clear_cookie("user")


class AuthLogoutHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        self.clear_cookie("user")
        self.write({"status": "ok", "info": "User logged out"})


def make_app():
    return tornado.web.Application(
        handlers=[
            (r"/api/upload", UploadUrlsHandler),
            (r"/api/status", GetStatusHandler),
            (r"/api/register", RegisterHandler),
            (r"/api/login", AuthLoginHandler),
            (r"/api/logout", AuthLogoutHandler),
        ],
        **{
            "cookie_secret": settings.COOKIE_SECRET,
            "login_url": "/api/login",
            "debug": True,
        },
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)

    DB_MANAGER.create_all()

    polling = tornado.ioloop.PeriodicCallback(
        lambda: PUBLISHER.process_data_events(), 1000
    )
    polling.start()

    tornado.ioloop.IOLoop.current().start()
