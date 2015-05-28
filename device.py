import pexpect
import re
import time
from bluepy.btle import Peripheral


class Device:
    _characteristics = {}
    _peripheral = None

    def __init__(self, characteristics):
        self._characteristics = characteristics

    def discover(self, nameFilter, uuid):
        devices = self._scan(nameFilter=nameFilter)
        self._connect(devices[0]['addr'], uuid)

    def _scan(self, nameFilter, hciName='hci0', timeout=3):
        conn = None
        conn = pexpect.spawn('hciconfig %s reset' % hciName)
        time.sleep(0.2)
        conn = pexpect.spawn('timeout %d hcitool lescan' % timeout)
        time.sleep(0.2)

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
        lines = [line for line in lines if re.match(nameFilter, line['name'])]

        if len(lines) != 1:
            raise Exception('%s not found' % nameFilter)

        return lines

    def _connect(self, address, uuid):
        if not address:
            return

        self._peripheral = Peripheral(deviceAddr=address)
        self._peripheral.discoverServices()
        mainService = self._peripheral.getServiceByUUID(uuid)
        for characteristicName in self._characteristics:
            characteristicDic = self._characteristics[characteristicName]
            characteristic = mainService.getCharacteristics(characteristicDic['uuid'])
            characteristicDic['handle'] = characteristic[0].valHandle

    def _disconnect(self):
        pass

    def writeCharacteristic(self, characteristicName, command):
        self._peripheral.writeCharacteristic(self._characteristics[characteristicName]['handle'], command)

