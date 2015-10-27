import sys
import threading
import Queue
import socket
import struct

import ps3_reader
import controller

QUEUE_LENGTH = 10
UDP_PERIOD = 0.1

class Server(object):
    def __init__(self, host, port):
        self.queue = Queue.Queue(QUEUE_LENGTH)
        self.controller = ps3_reader.PS3Controller(self.queue)
        self.controls = controller.Controls(0.0, 0.0, 0.0, 0.0)
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    def start(self):
        self.stop_event.clear()
        self.controller.start()
        self.get_controls_thread = threading.Thread(target=self.get_controls)
        self.get_controls_thread.start()
        th = threading.Timer(UDP_PERIOD, self.send_packet)
        th.start()

    def stop(self):
        self.stop_event.set()
        # Add a message to queue to flush the thread
        self.queue.put(controller.Controls(0.0, 0.0, 0.0, 0.0))

    def get_controls(self):
        while not self.stop_event.is_set():
            controls = self.queue.get()
            self.lock.acquire()
            self.controls = controls
            self.lock.release()

    def send_packet(self):
        self.lock.acquire()
        controls = self.controls
        self.lock.release()
        self.socket.sendto(struct.pack("ffff", *controls), (self.host, self.port))
        # Reset to send another packet
        if not self.stop_event.is_set():
            th = threading.Timer(UDP_PERIOD, self.send_packet)
            th.start()

def main():
    server = Server("127.0.0.1", 6969)
    server.start()

if __name__ == "__main__":
    main()
