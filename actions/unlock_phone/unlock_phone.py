from actions.base import BaseGame


class UnlockPhone(BaseGame):
    def __init__(self, boy):
        super().__init__(boy, action_name='unlock_phone')

    def unlock(self):
        if self.check_screen('lock'):
            screen_gray = self.boy.get_screen_gray()
            resolution = screen_gray.size
            width, height = resolution
            self.boy.swipe(start=(int(width / 2), int(height / 2)), end=(int(width), int(height / 2 - 100)))
            self.boy.long_press(int(width), int(height / 2 - 100))

    def run(self):
        self.unlock()
