from actions.basic_play.basic_play import BasicPlay
from utils.android_boy import AndroidBoy


class Twd:
    def __init__(self, serial, app_package, tool_type):
        boy = AndroidBoy(serial=serial, app_package=app_package)
        self.basic_play = BasicPlay(boy)
        self.start(tool_type)

    def start(self, tool_type):
        if tool_type == 'basic_play':
            while True:
                self.basic_play.run()