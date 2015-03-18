'''
RFID daemon
===========
'''

__all__ = ('RfidDaemon', )

import sys
from time import sleep
from os.path import dirname, join, realpath

sys.path += [realpath(join(dirname(__file__), 'libs'))]

import pynfc
from collections import deque
from threading import Thread
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.event import EventDispatcher

class RfidDaemon(Thread, EventDispatcher):
    def __init__(self):
        EventDispatcher.__init__(self)
        self.register_event_type('on_uid')
        Thread.__init__(self)
        self.daemon = True
        self.q = deque()
        self.quit = False
        Clock.schedule_interval(self._poll_queue, 1 / 5.)

    def on_uid(self, value):
        return

    def _poll_queue(self, dt):
        while True:
            try:
                uid = self.q.pop()
            except IndexError:
                return
            self.dispatch('on_uid', uid)

    def stop(self):
        self.quit = True
        self.join()

    def _connect(self):
        Logger.info('Rfid: Search devices...')
        try:
            devs = pynfc.list_devices()
            Logger.info('Rfid: Found %d devices' % len(devs))
            if not devs:
                Logger.error('Rfid: No devices found, will retry later.')
                return None, None
            dev = devs[0]
            Logger.info('Rfid: Device %r using driver %r' % (
                dev.device, dev.driver))
            nfc = dev.connect(target=False)
            return dev, nfc
        except:
            return None, None

    def run(self):
        dev = nfc = None
        mod_targets = None
        add = self.q.appendleft
        current_uids = []
        while not self.quit:

            # create device
            if not dev:
                dev, nfc = self._connect()
                if dev is None:
                    sleep(5)
                    continue
                mod_targets = (
                    pynfc.Modulation(nmt=nfc.NMT_ISO14443A, nbr=nfc.NBR_106),
                    pynfc.Modulation(nmt=nfc.NMT_ISO14443B, nbr=nfc.NBR_106),
                )
                nfc.configure(nfc.NDO_INFINITE_SELECT, False)

            if dev:
                error = nfc.get_error()
                if 'error' in error:
                    Logger.error('Rfid: An error occured %r' % error)
                    dev = nfc = None
                    continue

            # NFC library polling
            Logger.trace('Rfid: Polling target')
            targets = nfc.poll_targets(mod_targets, 1, 2)
            Logger.trace('Rfid: Read %d targets' % len(targets))
            uids = []
            for target in targets:
                uid = self._read_uid(target)
                uids.append(uid)
                if not uid in current_uids:
                    add(uid)
                    current_uids.append(uid)
                else:
                    continue

            # remove old uid to accept further discovery
            for uid in current_uids[:]:
                if uid not in uids:
                    current_uids.remove(uid)

            sleep(1)

    def _read_uid(self, target):
        nai = target.nti.nai
        uid = ''.join(map(lambda x: '%02x' % int(x), nai.uid[:nai.uidlen]))
        return uid.lower()
