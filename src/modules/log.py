import logging
import modules.utils

class WebSocketLogger(logging.StreamHandler):

    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    
    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    def emit(self, record):
        try:
            packet = {'category': 'log', 'message': self.format(record), 'type': record.levelno}
            self.listener.send_data(modules.utils.getJSON(packet))
            self.flush()
        except NameError:
            print('The server thread has not been created yet. Dropping log output.')
        except:
            self.handleError(record)

        