#!/usr/bin/python
import logging, modules.utils

class WebSocketLogger(logging.Handler):

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
            
class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno  == logging.WARNING:
            # display yellow text
            record.msg = '\033[93m\033[1m%s\033[0m\033[39m' % (record.msg)
        elif record.levelno == logging.ERROR:
            # display red text
            record.msg = '\033[31m\033[1m%s\033[0m\033[39m' % (record.msg)
        elif record.levelno == logging.INFO:
            # display blue text
            record.msg = '\033[94m\033[1m%s\033[0m\033[39m' % (record.msg)
        elif record.levelno == logging.CRITICAL:
            # display bold red text
            record.msg = '\033[31m\033[1m%s\033[0m\033[39m' % (record.msg)
        elif record.levelno == logging.DEBUG:
            # display green text
            record.msg = '\033[92m\033[1m%s\033[0m\033[39m' % (record.msg)
            
        return super(ConsoleFormatter , self).format(record)


        