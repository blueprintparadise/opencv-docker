from datetime import datetime
from time import sleep
from threading import Thread
import logging


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)

INFORMATION = '/proc/net/dev'
MBITS = float(1024 * 1024)


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
        tx = float(tx_bytes - self.tx_bytes) / interval
        rx = float(rx_bytes - self.rx_bytes) / interval

        log.info('tx_bytes: %5.2f Mbps (%f bps) rx_bytes: %5.2f Mbps (%f bps)' % (tx / MBITS, tx, rx / MBITS, rx))
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
