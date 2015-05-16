#!/usr/bin/python
import threading

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_flag = threading.Event()

    """
    # Sample implementation of a run() method

    def run(self):
        while True:
            if self.stopped():
                break;
            # Program logic goes here
    """

    def stop(self):
        self._stop_flag.set()

    def stopped(self):
        return self._stop_flag.isSet()