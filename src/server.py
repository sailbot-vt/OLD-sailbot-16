import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

wss = []

class WSHandler(tornado.websocket.WebSocketHandler):
    
    def check_origin(self, origin):
        return True
    
    def open(self):
        print 'New connection established.'
        if self not in wss:
            wss.append(self)
      
    def on_message(self, message):
        print 'Received message: %s' % message
 
    def on_close(self):
        print 'Connection closed.'
        if self in wss:
            wss.remove(self)

def wsSend(message):
    for ws in wss:
        ws.write_message(message);
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])

def schudule_func():
    # called periodically
    wsSend("Ping!")
 
if __name__ == "__main__":
    print "Starting server."
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(4041)
    
    # creates a periodic callback function
    interval_ms = 1000
    main_loop = tornado.ioloop.IOLoop.instance()
    sched = tornado.ioloop.PeriodicCallback(schudule_func(), interval_ms, io_loop = main_loop)
    
    # starts the callback and the main IO loop
    sched.start()
    main_loop.start()
