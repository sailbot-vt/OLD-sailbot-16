#!/usr/bin/python
import logging, modules.utils, curses

class WebSocketLogger(logging.Handler):
    def __init__(self, listener):
        super().__init__()
        self.listener = listener

    def emit(self, record):
        try:
            packet = {
                'category': 'log',
                'message': self.format(record),
                'type': record.levelno
            }
            self.listener.send_data(modules.utils.getJSON(packet))
            self.flush()
        except NameError:
            # The server thread has not been created yet. Dropping log output.
            pass
        except:
            self.handleError(record)

class CursesHandler(logging.Handler):
    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen

        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def emit(self, record):
        try:
            screen = self.screen
            screen.addstr(u'\n%s' % self.format(record), self.get_color_pair(record.levelno))
            screen.refresh()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def get_color_pair(self, level):
        index = str(level)
        return curses.color_pair({
            '10': 83,
            '20': 39,
            '30': 245,
            '40': 167,
            '50': 197
        }[index])
