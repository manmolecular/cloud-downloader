import json
from logging import DEBUG
from mimetypes import guess_type
from os import environ
from pathlib import Path
from sys import exit
from uuid import uuid4
from random import choice
from string import ascii_letters

import tornado.escape
import tornado.ioloop
import tornado.iostream
import tornado.log
import tornado.process
import tornado.web

import settings
from database.crud import DbManager
from database.schemas import User, Task
from handlers.files import FilesHandler
from publisher.publisher import Publisher

# Set logging level for Tornado Server
tornado.log.access_log.setLevel(DEBUG)

# Define default variables and objects
DATA_PATH = Path("data")
FILES_HANDLER = FilesHandler()
RABBIT_MQ_HOST = environ.get("RABBITMQ_HOST") or "localhost"

print(f"Use {RABBIT_MQ_HOST} as RabbitMQ host")

# Create Publisher connection
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
# Also create Database manager connection
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
        if not self.get_secure_cookie("user"):
            self.write({"status": "fail", "info": "User not logged in"})
            return
        uuid = self.get_argument("uuid", None)
        self.write(
            {
                "status": "ok",
                "info": DB_MANAGER.get_task_status(uuid) or "Not exists",
                "uuid": uuid,
            }
        )


class UploadUrlsHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        self.write(
            {
                "status": "ok",
                "info": "Upload list of URLs with POST method into the cloud",
            }
        )

    async def post(self):
        if not self.get_secure_cookie("user"):
            self.write({"status": "fail", "info": "User not logged in"})
            return
        url_list = json.loads(self.request.body)
        uuid = str(uuid4())
        PUBLISHER.publish_task(url_list, uuid)
        task_schema = Task(**{"uuid": uuid, "urls": json.dumps(url_list), "status": "in progress"})
        DB_MANAGER.create_task(task_schema)
        self.write({"status": "ok", "info": "Task created", "uuid": uuid})


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
            self.set_secure_cookie(
                "user", "".join(choice(ascii_letters) for _ in range(10))
            )
        else:
            self.clear_cookie("user")


class AuthLogoutHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        self.clear_cookie("user")
        self.write({"status": "ok", "info": "User logged out"})


class ListHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        if not self.get_secure_cookie("user"):
            self.write({"status": "fail", "info": "User not logged in"})
            return
        # If we got UUID to get files for, return results only for UUID
        uuid = self.get_argument("uuid", None)
        if uuid:
            self.write(
                {
                    "status": DB_MANAGER.get_task_status(uuid)
                    or "Task does not exists",
                    "files": FILES_HANDLER.get_files_by_uuid(uuid)
                    or "Files not exists",
                    "urls": DB_MANAGER.get_task_urls(uuid)
                    or "URLs not exists",
                }
            )
            return
        # Else, if we don't have UUID - list all the possible UUIDs
        try:
            response = {}
            for uuid in DB_MANAGER.get_task_uuids():
                uuid_id = uuid[0]
                uuid_files = [
                    filename.name
                    for filename in list(DATA_PATH.rglob("*.*"))
                    if uuid_id in str(filename)
                ]
                response[uuid_id] = {
                    "status": DB_MANAGER.get_task_status(uuid)
                    or "Task does not exists",
                    "files": uuid_files
                    or "Files not exists",
                    "urls": DB_MANAGER.get_task_urls(uuid)
                    or "URLs not exists",
                }
            self.write(response)
        except:
            self.write(
                {
                    "status": "fail",
                    "info": "List of downloads is empty. Try to download something first.",
                }
            )


class DownloadHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        pass

    @staticmethod
    def _check_for_path_traversal(root_dir: str or Path, relative_path: str or Path):
        try:
            Path(root_dir).joinpath(relative_path).resolve().relative_to(
                root_dir.resolve()
            )
        except AttributeError:
            return
        return Path(root_dir).joinpath(relative_path)

    async def get(self):
        if not self.get_secure_cookie("user"):
            self.write({"status": "fail", "info": "User not logged in"})
            return
        uuid = self.get_argument("uuid", None)
        filename = self.get_argument("filename", None)
        try:
            with open(
                file=self._check_for_path_traversal(DATA_PATH, f"{uuid}/{filename}"),
                mode="rb",
            ) as file:
                self.set_header(
                    "Content-Type",
                    guess_type(url=filename, strict=False)[0]
                    or "application/force-download",
                )
                while True:
                    chunk = file.read(2048)
                    if not chunk:
                        break
                    try:
                        self.write(chunk)
                        await self.flush()
                    except tornado.iostream.StreamClosedError:
                        break
                    finally:
                        del chunk
        except Exception as e:
            print(e)
            self.write({"status": "fail", "info": "UUID or file not exists"})


def make_app():
    return tornado.web.Application(
        handlers=[
            (r"/api/upload", UploadUrlsHandler),
            (r"/api/status", GetStatusHandler),
            (r"/api/register", RegisterHandler),
            (r"/api/login", AuthLoginHandler),
            (r"/api/logout", AuthLogoutHandler),
            (r"/api/list", ListHandler),
            (r"/api/download", DownloadHandler),
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

    try:
        DB_MANAGER.create_all()
    except:
        print("Database connection is not initialized")
        exit(1)

    polling = tornado.ioloop.PeriodicCallback(
        lambda: PUBLISHER.process_data_events(), 1000
    )
    polling.start()

    tornado.ioloop.IOLoop.current().start()
