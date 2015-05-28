import time
import math
# import config
import signal
from device import Device
from datetime import datetime

class YeeLightBlue:
    _characteristics = {
        'CONTROL': {
            'uuid': 'fff1',
            'handle': None,
            'length': 18
        },
        'COLOR_FLOW': {
            'uuid': 'fff7',
            'handle': None,
            'length': 20
        },
        'EFFECT': {
            'uuid': 'fffc',
            'handle': None,
            'length': 2
        },
    }
    _device = None

    def __init__(self):
        self._device = Device(self._characteristics)
        self._discover()

    def _discover(self):
        try:
            self._device.discover('^Yeelight.*', 'fff0')
        except Exception as e:
            print 'rescan for YeeLightBlue... (%s)' % str(datetime.now())
            self._discover()

    def turnOn(self):
        try:
            self._writeCharacteristic('CONTROL', '{0},{1},{2},{3}'.format(255, 255, 255, 100))
        except Exception as e:
            print 'turn on failed at %s' % str(datetime.now())

    def turnOff(self):
        try:
            self._writeCharacteristic('CONTROL', '{0},{1},{2},{3}'.format(0, 0, 0, 0))
        except Exception as e:
            print 'turn off failed at %s' % str(datetime.now())

    def setColor(self, red, green, blue, brightness=100):
        try:
            self._writeCharacteristic('CONTROL', '{0},{1},{2},{3}'.format(red, green, blue, brightness))
        except Exception as e:
            print 'set color failed at %s' % str(datetime.now())

    def flash(self, timeout, red, green, blue, useColorFlow):
        try:
            class TimeoutError(Exception):
                pass
            def handler(signum, frame):
                raise TimeoutError
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            try:
                if useColorFlow:
                    self._colorFlow(red, green, blue)
                else:
                    self._colorFlash(red, green, blue)
            except TimeoutError:
                if useColorFlow:
                    self._writeCharacteristic('COLOR_FLOW', 'CE')  # complete color flow command
            finally:
                signal.alarm(0)
        except Exception as e:
            print 'flash failed at %s' % str(datetime.now())

    def _colorFlow(self, red, green, blue):
        self._setMode('TS')
        self._writeCharacteristic('COLOR_FLOW', '{0},{1},{2},{3},{4},{5}'.format(0, red, green, blue, 100, 1))
        if red != 0:
            red = abs(red - 255)
        if green != 0:
            green = abs(green - 255)
        if blue != 0:
            blue = abs(blue - 255)
        self._writeCharacteristic('COLOR_FLOW', '{0},{1},{2},{3},{4},{5}'.format(1, red, green, blue, 100, 1))
        self._writeCharacteristic('COLOR_FLOW', 'CB')
        while True:
            pass  # waiting timeout

    def _colorFlash(self, red, green, blue):
        self._setMode('TE')
        i = 0
        while True:
            sin = (math.sin(i) + 1) / 2
            self.setColor(int(red * sin), int(green * sin), int(blue * sin))
            time.sleep(0.01)
            i += 0.1

    def _setMode(self, mode):
        if mode not in ['TE', 'TS']:  # TE: non-gradual, TS: gradual
            raise Exception('Invalid effect mode')
        self._writeCharacteristic('EFFECT', mode)

    def _writeCharacteristic(self, characteristicName, command):
        i = len(command)
        while i < self._characteristics[characteristicName]['length']:
            command += ','
            i += 1
        self._device.writeCharacteristic(characteristicName, command)

'''
    def timer(self, onStartFunction, onFinishFunction, timeout):
        class TimeoutError(Exception):
            pass
        def handler(signum, frame):
            raise TimeoutError
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        try:
            onStartFunction()
        except TimeoutError:
            onFinishFunction()
        finally:
            signal.alarm(0)
'''