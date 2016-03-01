import logging
import tornado.web
import tornado.ioloop
from lib import AppUtils

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
        self.render('test.html')