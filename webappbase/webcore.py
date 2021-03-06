import argparse
import errno
import json
import logging
import os
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.process
import tornado.web
from lib import AppUtils
from lib import Config
from lib import DatabaseUtils
from lib import RestAPIHandlers
from tornado.options import define, options

from webappbase.lib import WebHandlers

cwd = os.getcwd()
sys.path.append(cwd)


class Application(tornado.web.Application):
    def __init__(self, a_config):
        """
        Main application, external connections and services start here
        :param a_config: a config object from which necessary options can be retrieved
        """

        routes = [
            (r'/', WebHandlers.Home),
            (r'/alarm/([A-Za-z0-9]+)', WebHandlers.Alarm),
            (r'/test', WebHandlers.Test),
            (r'/api/alarm', RestAPIHandlers.Alarm),
            (r'/api/alarm/([A-Za-z0-9]+)', RestAPIHandlers.Alarm),
            (r'/api/heartbeat', RestAPIHandlers.Heartbeat),
            (r'/ws', WebHandlers.EchoWebSocket),
            (r'.*', WebHandlers.BaseHandler)
        ]

        # Define application settings
        settings = dict(
            title=config['client']['title'],
            template_path=config['client']['template_path'],
            static_path=config['client']['static_path'],
            debug=True,
        )
        # Define default port based on config or override via CLI
        define('port', default=config['server']['port'], help='run on the given port', type=int)
        super(Application, self).__init__(routes, **settings)

        # Setup Global Logging
        loglevel = getattr(logging, config['logging']['log_level'].upper())
        loglocation = config['logging']['log_location'] + config['logging']['log_name']
        logger = logging.getLogger(config['app']['name'])
        try:
            os.makedirs(config['logging']['log_location'])
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        logger.addHandler(logging.StreamHandler())
        logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(name)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename=loglocation, level=loglevel)
        logger.addHandler(logging.StreamHandler())

        # Start logging
        logger.info("Initializing @ " + AppUtils.getInstance())
        logger.debug("Processors: " + str(tornado.process.cpu_count()))

        # Single Database connection across all handlers
        self.database = DatabaseUtils.AppDatabase(config['database'])


def main():
    parser = argparse.ArgumentParser(
        prog='webcore',
        description='''
            Web application core library - webcore.py
        '''
    )
    # Only supports file config for now
    parser.add_argument('-c', '--config', help='path to a config file')
    parser.add_argument('-p', '--port', help='listen port, overrides port in config if set\n(Default: 8000)')

    args = parser.parse_args()
    if not args.config:
        parser.print_help()
        sys.exit(1)
    config = Config(args.config)
    # http_server = tornado.httpserver.HTTPServer(Application())
    # http_server.listen(options.port)
    # tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
