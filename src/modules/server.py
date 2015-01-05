#!/usr/bin/python

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading
import os
import logging
from modules.data import Data

wss = []
locations = []


class WSHandler(tornado.websocket.WebSocketHandler):

    """ Creates the web socket server
    """

    def check_origin(self, origin):
        return True

    def open(self):
        logging.info('New connection established.')
        
        for marker in locations:
            location_data = Data(category="marker", type="buoy", location=marker)
            self.write_message(location_data.to_JSON())
        
        if self not in wss:
            wss.append(self)

    def on_message(self, message):
        logging.info('Received message: %s' % message)

    def on_close(self):
        logging.info('Connection closed.')
        if self in wss:
            wss.remove(self)


class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        self.render('../web/index.html')


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [(r'/ws', WSHandler), (r'/', IndexHandler)]
        settings = {'debug': True,
                    'static_path': os.path.join(os.path.dirname(__file__),
                    '../web')}
        tornado.web.Application.__init__(self, handlers, **settings)


application = Application()


class ServerThread(threading.Thread):

    """ Creates thread which runs the web socket server
    """
    def add_locations(self, markers):
        for marker in markers:
            locations.append(marker)
            
    def send_data(self, message):
        for ws in wss:
            # do not log any data here, doing so would create an infinite loop
            try:
                ws.write_message(message)
                break
            except TypeError:
                logging.error('Tried to send invalid value.')

    def close_sockets(self):
        logging.info('Closing all connections....')
        for ws in wss:
            ws.close()

    def run(self):
        logging.info('Starting server.')
            
        try:
            http_server = tornado.httpserver.HTTPServer(application)
            http_server.listen(self._kwargs['PORT'])

            main_loop = tornado.ioloop.IOLoop.instance()

            logging.info('The web server successfully bound to port %d'
                         % self._kwargs['PORT'])

            # starts the main IO loop

            main_loop.start()
        except OSError:

            logging.error('The web server failed to bind to the port!')
