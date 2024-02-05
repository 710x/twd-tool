from time import sleep

from actions.base import BaseGame


class BasicPlay(BaseGame):
    def __init__(self, boy):
        super().__init__(boy, action_name='basic_play')

    def is_home(self):
        result = self.check_screen('inventory') and self.check_screen('start')
        print('is_home: ' + str(result))
        return result

    def empty_space(self):
        while self.check_screen('empty_space'):
            self.find_and_click('empty_space')
            sleep(1)

    def back_world(self):
        while not self.is_home():
            # if self.check_screen('light_world') or self.check_screen('world') or self.check_screen('back') or self.check_screen('empty_space'):
            self.find_and_click('back')
            self.find_and_click('world')
            self.empty_space()

    def play(self):
        if self.is_home():
            self.find_and_click('start')
            sleep(2)
            self.find_and_click('start')
            sleep(5)
            self.find_and_click('start_2')
            sleep(10)
            while self.check_screen('auto'):
                sleep(5)
            if self.find_and_click('victory'):
                self.find_and_click('continue')
            elif self.find_and_click('defeat'):
                self.find_and_click('play_again')
        else:
            if self.check_screen('start_2'):
                self.find_and_click('start_2')
                while self.check_screen('auto'):
                    sleep(5)
                if self.find_and_click('victory'):
                    self.find_and_click('continue')
                elif self.find_and_click('defeat'):
                    self.find_and_click('play_again')
            else:
                self.back_world()
        sleep(5)

    def run(self):
        self.play()
