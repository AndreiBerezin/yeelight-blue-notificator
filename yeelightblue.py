import pexpect
import re
import time
from bluepy.btle import Peripheral
import math
# import config
# import logging
import signal


class YeeLightBlue:
    def __init__(self):
        self.characteristics = {
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
        self.peripheral = None

        # self.logger = None
        # self._initLogger()

        try:
            devices = self._scan()
            self._connect(devices[0]['addr'])
        except Exception as e:
            print e.message + '; rescan for YeeLightBlue...'
            self.__init__()

    # def _initLogger(self):
    #     self.logger = logging.getLogger('YeeLightBlue')
    #     self.logger.setLevel(logging.WARNING)
    #
    #     logfile = '{0}/{1}'.format(config.LOG_DIR, config.LOG_MAIN_FILE)
    #     handler = logging.FileHandler(logfile)
    #     self.logger.addHandler(handler)

    def turnOn(self):
        self._writeCharacteristic('CONTROL', '{0},{1},{2},{3}'.format(255, 255, 255, 100))

    def turnOff(self):
        self._writeCharacteristic('CONTROL', '{0},{1},{2},{3}'.format(0, 0, 0, 0))

    def setColor(self, red, green, blue, brightness=100):
        self._writeCharacteristic('CONTROL', '{0},{1},{2},{3}'.format(red, green, blue, brightness))

    def flash(self, timeout, red, green, blue, useColorFlow):
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
            pass
        finally:
            signal.alarm(0)


    def _scan(self, hci_name='hci0', name_filter='^Yeelight.*', timeout=3):
        # self.logger.warn('start scan')
        conn = None
        try:
            conn = pexpect.spawn('hciconfig %s reset' % hci_name)
            time.sleep(0.2)

            conn = pexpect.spawn('timeout %d hcitool lescan' % timeout)
            time.sleep(0.2)
        except Exception:
            return

        conn.expect('LE Scan \.+', timeout=timeout)
        output = ''
        line_pat = '(?P<addr>([0-9A-F]{2}:){5}[0-9A-F]{2}) (?P<name>.*)'
        while True:
            try:
                res = conn.expect(line_pat)
                output += conn.after
            except pexpect.EOF:
                break

        lines = re.split('\r?\n', output.strip())
        lines = list(set(lines))
        lines = [line for line in lines if re.match(line_pat, line)]
        lines = [re.match(line_pat, line).groupdict() for line in lines]
        lines = [line for line in lines if re.match(name_filter, line['name'])]

        if len(lines) != 1:
            raise Exception('YeeLightBlue not found')

        return lines

    def _connect(self, address):
        if not address:
            return

        self.periferal = Peripheral(deviceAddr=address)
        self.periferal.discoverServices()
        mainService = self.periferal.getServiceByUUID('fff0')
        for charName in self.characteristics:
            characteristic = self.characteristics[charName]
            char = mainService.getCharacteristics(characteristic['uuid'])
            characteristic['handle'] = char[0].valHandle

    def _disconnect(self):
        pass

    def _setMode(self, mode):
        if mode not in ['TE', 'TS']:  # TE: non-gradual, TS: gradual
            raise Exception('Invalid effect mode')
        self._writeCharacteristic('EFFECT', mode)

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

    def _writeCharacteristic(self, charName, command):
        i = len(command)
        characteristic = self.characteristics[charName]
        while i < characteristic['length']:
            command += ','
            i += 1
        self.periferal.writeCharacteristic(characteristic['handle'], command)
        pass

