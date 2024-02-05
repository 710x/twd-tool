from utils.android_boy import AndroidBoy


class BaseGame:
    def __init__(self, boy, action_name='base'):
        self.res_dir = fr'actions/{action_name}/res'
        if isinstance(boy, AndroidBoy):
            self.boy = boy

    def res_path(self, temp):
        return fr'{self.res_dir}/{temp}.png'

    def check_screen(self, temp):
        return self.boy.check_screen(temp=self.res_path(temp=temp))

    def find_and_click(self, temp, delta=None):
        if delta:
            return self.boy.find_and_click(temp=self.res_path(temp), delta=delta)
        return self.boy.find_and_click(temp=self.res_path(temp=temp))

