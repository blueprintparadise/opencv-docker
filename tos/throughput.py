from datetime import datetime
from time import sleep
from threading import Thread

INFORMATION = '/proc/net/dev'


class Throughput(Thread):
    """thread to send message to the image processing server"""

    def __init__(self, interval, intf_name='wlan0'):
        """interval: period in seconds """
        self.interval = interval
        self.intf_name = intf_name
        super(Throughput, self).__init__()

    def get_bytes(self):
        tx_bytes, rx_bytes = (None, None)
        with open(INFORMATION, 'r') as f:
            for line in f:
                line = line.split()
                achou = line[0].find(self.intf_name + ':') >= 0
                if len(line) > 0 and achou:
                    tx_bytes = int(line[9])
                    rx_bytes = int(line[1])
        return tx_bytes, rx_bytes

    def get_throughput(self):
        now = datetime.now()
        tx_bytes, rx_bytes = self.get_bytes()
        interval = (now - self.t).total_seconds()
        print('tx_bytes: %f rx_bytes: %f' %
              (float(tx_bytes - self.tx_bytes) / interval,
               float(rx_bytes - self.rx_bytes) / interval)
              )
        self.t, self.tx_bytes, self.rx_bytes = (now, tx_bytes, rx_bytes)

    def run(self):
        self.t = datetime.now()
        self.tx_bytes, self.rx_bytes = self.get_bytes()
        self.run = True
        while self.run:
            sleep(self.interval)
            self.get_throughput()

    def stop(self):
        self.run = False


if __name__ == '__main__':
    t = Throughput(interval=1.0)
    t.start()
