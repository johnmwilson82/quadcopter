import sys
import socket
import collections
import threading
import struct
import fcntl

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


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                            0x8915,
                            struct.pack('256s', ifname[:15]))[20:24])

def main():
    if_ip = get_interface_ip("wlan0")
    sys.stdout.write("Listening on %s...\n" % if_ip)
    client = Client(if_ip, 6969)
    client.start()

if __name__ == "__main__":
    main()
