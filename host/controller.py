import threading
import collections

Controls = collections.namedtuple(
    'Controls', ['yaw', 'pitch', 'roll', 'throttle']
)

class Controller(object):
    def __init__(self, queue):
        self.stop_event = threading.Event()
        self.queue = queue

    def start(self):
        self.stop_event.clear()
        th = threading.Thread(target=self.read_loop)
        th.start()

    def stop(self):
        self.stop_event.set()
