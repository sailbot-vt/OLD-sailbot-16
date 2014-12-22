from tornado import httpserver
from tornado import websocket
from tornado import ioloop
from tornado import web
 
 
class WSHandler(websocket.WebSocketHandler):
    def open(self):
        print ("new connection");
        self.write_message("Hello World")
      
    def on_message(self, message):
        print ('message received %s' % message);
 
    def on_close(self):
      print ('connection closed')
 
 
application = web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = httpserver.HTTPServer(application)
    http_server.listen(4041)
    ioloop.IOLoop.instance().start()