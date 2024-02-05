from time import sleep

from actions.unlock_phone.unlock_phone import UnlockPhone
from utils.android_boy import AndroidBoy


class Phone:
    def __init__(self, serial, app_package):
        boy = AndroidBoy(serial=serial, app_package=app_package)
        self.unlock_phone = UnlockPhone(boy)
        self.start()

    def start(self):
        while True:
            self.unlock_phone.run()
            sleep(30)
