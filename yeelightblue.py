import pexpect
import re
import time

class YeeLightBlue:
    def __init__(self):
        self.peripheral = None
        self.address = None

        devices = self.scan()
        if (len(devices) != 1):
            raise Exception("YeeLightBlue not found")
        else:
            self.address = devices[0]['addr']

    def scan(hci_name='hci0', name_filter='^Yeelight.*', timeout=3):
        conn = pexpect.spawn('hciconfig %s reset' % hci_name)
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
        lines = [line for line in lines if re.match(name_filter, line['name'])]

        return lines

    def _connect(self, address):
        pass

    def _disconnect(self):
        pass

    def turnOn(self):
        pass

    def turnOff(self):
        pass

    def setColor(self, red, green, blue, brightness):
        pass

