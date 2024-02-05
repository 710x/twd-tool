from time import sleep

from actions.base import BaseGame


class InitGame(BaseGame):
    def __init__(self, boy):
        super().__init__(boy, action_name='init_game')

    def start_game(self):
        self.boy.start_if_not_running()

    def ignore(self):
        while self.check_screen('ignore'):
            self.find_and_click('ignore')
            sleep(1)

    def click_to_start(self):
        while self.check_screen('click_to_start'):
            self.find_and_click('click_to_start')
            sleep(1)

    def click_ok_to_download(self):
        if self.check_screen('cancel_ok'):
            self.find_and_click('ok')

    def empty_space(self):
        while self.check_screen('empty_space'):
            self.find_and_click('empty_space')
            sleep(1)

    def get_assets(self):
        if self.check_screen('start'):
            self.find_and_click('start', (0, -60))
            self.empty_space()

    def is_home(self):
        return self.check_screen('inventory') and self.check_screen('start')

    def back_world(self):
        while not self.is_home():
            if self.check_screen('light_world') or self.check_screen('world') or self.check_screen('back'):
                self.find_and_click('back')
                self.find_and_click('light_world')
                self.find_and_click('world')
                self.empty_space()

    def run(self):
        self.start_game()
        self.ignore()
        self.click_to_start()
        self.click_ok_to_download()
        self.empty_space()
        if self.is_home():
            self.get_assets()
            self.empty_space()
        self.back_world()
        return self.is_home()
