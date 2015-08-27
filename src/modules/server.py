#!/usr/bin/python
import tornado.httpserver, tornado.websocket, tornado.ioloop, tornado.web
import threading, os, logging, modules.utils
from modules.control_thread import StoppableThread

logger = logging.getLogger('log')

wss = target_locations = boundary_locations = []
http_server = main_loop = None

class WSHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        logger.info('New connection established.')

        for marker in target_locations:
            location_data = {'category': 'marker', 'type': 'target', 'location': marker}
            self.write_message(modules.utils.getJSON(location_data))

        for marker in boundary_locations:
            location_data = {'category': 'marker', 'type': 'boundary', 'location': marker}
            self.write_message(modules.utils.getJSON(location_data))

        if self not in wss:
            wss.append(self)

    def on_message(self, message):
        logger.info('Received message: %s' % message)

    def on_close(self):
        logger.info('Connection closed')
        if self in wss:
            wss.remove(self)


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('../web/index.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r'/ws', WSHandler), (r'/', IndexHandler)]
        settings = {
            'debug': True,
            'static_path': os.path.join(os.path.dirname(__file__),
            '../web')
        }
        tornado.web.Application.__init__(self, handlers, **settings)

application = Application()

class ServerThread(StoppableThread):
    def send_data(self, message):
        for ws in wss:
            # Do not log any data here, doing so would create an infinite loop
            try:
                ws.write_message(message)
                break
            except TypeError:
                logger.error('Tried to send invalid value.')

    def close_sockets(self):
        logger.info('Closing all connections...')
        for ws in wss:
            ws.close()

    def run(self):
        global target_locations, boundary_locations

        logger.info('Starting server')

        # Defining the locations array
        target_locations = self._kwargs['target_locations']
        boundary_locations = self._kwargs['boundary_locations']

        try:
            global http_server, main_loop

            http_server = tornado.httpserver.HTTPServer(application)
            http_server.listen(int(self._kwargs['port']))
            main_loop = tornado.ioloop.IOLoop.instance()

            def shutdown():
                if self.stopped():
                    logger.warning('Stopping HTTP server.')
                    self.close_sockets()
                    http_server.stop()
                    main_loop.stop()

            scheduler = tornado.ioloop.PeriodicCallback(shutdown, 500, io_loop = main_loop)
            scheduler.start()
            logger.info('The web server successfully bound to port %d' % self._kwargs['port'])
            main_loop.start()

        except OSError:
            logger.critical('The web server failed to bind to the port!')
