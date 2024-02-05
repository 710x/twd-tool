import os
import threading
from multiprocessing.pool import ThreadPool

import adbutils
from dotenv import load_dotenv

from bot import Twd
from phone import Phone

load_dotenv()
APP_PACKAGE = os.getenv("APP_PACKAGE")
IP_LIST = os.getenv("IP_LIST").split(",")
TOOL_TYPE = os.getenv("TOOL_TYPE")


def create_twd(lock, serial):
    Twd(serial=serial, app_package=APP_PACKAGE, tool_type=TOOL_TYPE)


def create_phone(lock, serial):
    Phone(serial=serial, app_package=APP_PACKAGE)


def create_threads(lock):
    pool = ThreadPool(processes=len(IP_LIST))
    twds = []
    phones = []
    for addr in IP_LIST:
        adb = adbutils.AdbClient('127.0.0.1', 5037)
        for d in adb.device_list():
            twds.append(pool.apply_async(create_twd, (lock, d.serial)))
            phones.append(pool.apply_async(create_phone, (lock, d.serial)))
    pool.close()  # Done adding tasks.
    pool.join()


if __name__ == '__main__':
    lock = threading.Lock()
    create_threads(lock)
