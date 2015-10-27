import evdev
import collections
import Queue

import controller

class PS3Controller(controller.Controller):
    Axes = collections.namedtuple(
        'Axes', ['lx', 'ly', 'rx', 'ry', 'lt', 'rt']
    )
    def __init__(self, queue):
        super(PS3Controller, self).__init__(queue)

        # define defaults
        self.lx_val = 0.0
        self.rx_val = 0.0
        self.ly_val = 0.0
        self.ry_val = 0.0
        self.lt_val = 0.0
        self.rt_val = 0.0

        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for dev in devices:
            if dev.name == 'Xbox Gamepad (userspace driver)':
                self.dev = dev
                return

        raise RuntimeError("No controller found (check xboxdrv loaded)")

    def parse_event(self, event):
        max_joystick = 32768
        max_throttle = 255
        if event.type == evdev.ecodes.EV_KEY:
            pass
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_X:
                self.lx_val = event.value * 1.0 / max_joystick
            elif event.code == evdev.ecodes.ABS_Y:
                self.ly_val = event.value * 1.0 / max_joystick
            elif event.code == evdev.ecodes.ABS_RX:
                self.rx_val = event.value * 1.0 / max_joystick
            elif event.code == evdev.ecodes.ABS_RY:
                self.ry_val = event.value * 1.0 / max_joystick
            elif event.code == evdev.ecodes.ABS_GAS:
                self.rt_val = event.value * 1.0 / max_throttle
            elif event.code == evdev.ecodes.ABS_BRAKE:
                self.lt_val = event.value * 1.0 / max_throttle
            return self.Axes(self.lx_val,
                             self.ly_val,
                             self.rx_val,
                             self.ry_val,
                             self.lt_val,
                             self.rt_val)

    def read_loop(self):
        for event in self.dev.read_loop():
            axes = self.parse_event(event)
            if not axes:
                continue
            controls = controller.Controls(
                yaw=axes.lx,
                pitch=axes.ry,
                roll=axes.rx,
                throttle=axes.rt,
            )

            if self.stop_event.is_set():
                break

            self.queue.put(controls)
