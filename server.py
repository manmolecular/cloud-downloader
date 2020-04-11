import tornado.ioloop
import tornado.web
import tornado.process
import tornado.escape
import json
from publisher.publisher import Publisher
from database.crud import DbManager
from database.schemas import User, Task
import settings

publisher = Publisher()
manager = DbManager()


class GetStatusHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        if self.get_secure_cookie("user"):
            uuid = self.get_argument("uuid", None)
            self.write({"status": "ok", "info": manager.get_task_status(uuid) or "Not exists", "uuid": uuid})
        else:
            self.write({"status": "fail", "info": "User not logged in"})


class DownloadUrlsHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def get(self):
        self.write({"status": "ok", "info": "Download list of URLs with POST method"})

    def post(self):
        if self.get_secure_cookie("user"):
            url_list = json.loads(self.request.body)
            uuid = publisher.publish_task(url_list)
            task_schema = Task(**{"uuid": uuid, "status": "in progress"})
            manager.create_task(task_schema)
            self.write({"status": "ok", "info": "Task created", "uuid": uuid})
        else:
            self.write({"status": "fail", "info": "User not logged in"})


class RegisterHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def post(self):
        user_schema = User(**json.loads(self.request.body))
        manager.create_user(user_schema)
        self.write({"status": "ok", "info": "User registered"})


class AuthLoginHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def check_permission(self, user_schema):
        return manager.check_credentials(user_schema)

    def post(self):
        user_schema = User(**json.loads(self.request.body))
        username = user_schema.username
        auth = manager.check_credentials(user_schema)
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
            (r"/api/download", DownloadUrlsHandler),
            (r"/api/status", GetStatusHandler),
            (r"/api/register", RegisterHandler),
            (r"/api/login", AuthLoginHandler),
            (r"/api/logout", AuthLogoutHandler),
        ], **{
            "cookie_secret": settings.COOKIE_SECRET,
            "login_url": "/api/login",
            "debug": True,
        }
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)

    manager.create_all()

    polling = tornado.ioloop.PeriodicCallback(
        lambda: publisher.process_data_events(),
        1000)
    polling.start()

    tornado.ioloop.IOLoop.current().start()
