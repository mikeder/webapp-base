import logging
import tornado.websocket
import tornado.ioloop
from lib import AppUtils
from lib import BaseUtils


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request)
        self.logger = logging.getLogger(__name__)
        self.generator = AppUtils.Generator()
        self.stringutil = AppUtils.StringUtil()

    def write_error(self, status_code, **kwargs):
        self.render("error.html", error=status_code)

    # Properties provided by Application in hud-alarm.py
    @property
    def database(self):
        return self.application.database


class Alarm(tornado.web.RequestHandler):
    @property
    def database(self):
        return self.application.database

    def get(self, a_alarm_id):
        alarm = self.database.getAlarms(a_alarm_id)[0]
        self.render('alarm.html', alarm=alarm)


class Home(BaseHandler):
    def get(self):
        self.render('home.html')


class Test(BaseHandler):
    def get(self):
        self.write('1')


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")