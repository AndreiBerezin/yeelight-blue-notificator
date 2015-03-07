import pexpect
import re
import time
from bluepy.btle import UUID, Peripheral, DefaultDelegate
# import config
# import logging

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
        # self.__initLogger()

        devices = self.__scan()
        if len(devices) != 1:
            raise Exception('YeeLightBlue not found')
        else:
            self.__connect(devices[0]['addr'])

    # def __initLogger(self):
    #     self.logger = logging.getLogger('YeeLightBlue')
    #     self.logger.setLevel(logging.WARNING)
    #
    #     logfile = "{0}/{1}".format(config.LOG_DIR, config.LOG_MAIN_FILE)
    #     handler = logging.FileHandler(logfile)
    #     self.logger.addHandler(handler)

    def __scan(self, hci_name='hci0', name_filter='^Yeelight.*', timeout=3):
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

        return lines

    def __connect(self, address):
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

    def turnOn(self):
        self.__writeCharacteristic('CONTROL', "{0},{1},{2},{3}".format(255, 255, 255, 100))

    def turnOff(self):
        self.__writeCharacteristic('CONTROL', "{0},{1},{2},{3}".format(0, 0, 0, 0))

    def setColor(self, red, green, blue, brightness):
        self.__writeCharacteristic('CONTROL', "{0},{1},{2},{3}".format(red, green, blue, brightness))

    def __writeCharacteristic(self, charName, command):
        i = len(command)
        characteristic = self.characteristics[charName]
        while i < characteristic['length']:
            command += ','
            i += 1
        self.periferal.writeCharacteristic(characteristic['handle'], command)
        pass

