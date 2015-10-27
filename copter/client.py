import sys
import socket
import collections
import threading
import struct

Controls = collections.namedtuple(
    'Controls', ['yaw', 'pitch', 'roll', 'throttle']
)

class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.settimeout(3.0)
        self.controls = Controls(0.0, 0.0, 0.0, 0.0)

        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def start(self):
        self.stop_event.clear()
        self.socket.bind((self.host, self.port))
        th = threading.Thread(target=self.rx_packet)
        th.start()

    def stop(self):
        self.stop_event.set()

    def rx_packet(self):
        while not self.stop_event.is_set():
            control_struct, _ = self.socket.recvfrom(1024)
            controls = struct.unpack("ffff", control_struct)
            self.lock.acquire()
            self.controls = Controls(*controls)
            self.lock.release()

            sys.stdout.write("YAW=%f, PITCH=%f, ROLL=%f, THROT=%f\n" %
                             controls)

def main():
    client = Client("127.0.0.1", 6969)
    client.start()

if __name__ == "__main__":
    main()
