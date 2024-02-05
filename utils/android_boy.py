import math
from time import sleep

import adbutils
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

from utils.putils import get_project_root


class AndroidBoy:
    def __init__(self, serial, center_point=None, is_joystick_show=False, app_package=None):
        """
        Initializes an instance of the AndroidBoy class.

        Args:
            serial (str): The serial number of the Android device.
            center_point (tuple): The center point coordinates of the joystick.
            is_joystick_show (bool, optional): Indicates whether the joystick is shown. Defaults to False.
            app_package (str, optional): The package name of the Android app. Defaults to None.
        """
        self.serial = serial
        self.d = adbutils.device(serial=serial)
        if center_point:
            self.center_point = center_point
        self.is_joystick_show = is_joystick_show
        self.fail = 0
        if app_package:
            self.app_package = app_package

    def __reset__(self):
        """
        Resets the fail counter to zero.
        """
        self.fail = 0

    def start_game(self):
        return self.d.app_start(self.app_package)

    def start_if_not_running(self):
        if not self.check_app_is_running():
            self.start_game()
            sleep(60)

    def turn_off_android(self):
        """
        Turns off the Android device.
        """
        self.d = None

    def turn_on_android(self):
        """
        Turns on the Android device.
        """
        self.d = adbutils.device(serial=self.serial)

    def turn_on_screen(self):
        """
        Turns on the screen by simulating the key event for power button press.
        """
        self.d.shell('input keyevent 26')
        sleep(1)

    def get_device(self):
        """
        Returns the device associated with the AndroidBoy object.
        """
        return self.d

    def get_serial(self):
        """
        Returns the serial number of the Android Boy.
        """
        return self.serial

    def joystick(self, radius=0, degrees=0, duration=0.2):
        """
        Moves the joystick to a specified position.

        Args:
            radius (int): The radius of the joystick movement.
            degrees (int): The angle in degrees at which the joystick should be moved.
            duration (float): The duration of the swipe action in seconds.
        """
        point_with_radius = self.get_point_in_circle_with_angle(radius, degrees)

        if not self.is_joystick_show:
            self.d.swipe(self.center_point[0], self.center_point[1], point_with_radius[0],
                         point_with_radius[1], duration)
        else:
            self.d.swipe(point_with_radius[0], point_with_radius[1],
                         point_with_radius[0], point_with_radius[1], duration)

    def get_point_in_circle_with_angle(self, radius, angle):
        """
        Calculates the coordinates of a point on a circle given the radius and angle.

        Args:
            radius (float): The radius of the circle.
            angle (float): The angle in degrees.

        Returns:
            tuple: The coordinates (x, y) of the point on the circle.
        """
        return (
            self.center_point[0] + radius * math.cos(math.radians(angle)),
            self.center_point[1] + radius * math.sin(math.radians(angle)),
        )

    def click(self, button):
        """
        Clicks the specified button on the screen.

        Args:
            button (tuple): The coordinates (x, y) of the button to click.

        Returns:
            None
        """
        if button is not None:
            (x, y) = button
            self.d.click(x, y)
            sleep(1)

    @staticmethod
    def load_image(filename):
        """
        Load an image from the specified filename.

        Args:
            filename (str): The name of the image file.

        Returns:
            numpy.ndarray or None: The loaded image as a NumPy array, or None if the image could not be loaded.
        """
        root = get_project_root()
        path = fr'{root}\{filename}'
        img = cv2.imread(path, 0)

        if img is not None:
            return img
        return None

    @staticmethod
    def get_template_size(self, tpl_src):
        """
        Get the size of a template image.

        Args:
            tpl_src (str): The file path of the template image.

        Returns:
            tuple: A tuple containing the width and height of the template image.
        """
        template = self.load_image(tpl_src)
        w, h = template.shape[::-1]
        return w, h

    def find_by_template(self, temp, pos='center', p1=(0, 0), p2=(0, 0), screen=None,
                         threshold=0.8):
        """
            Finds occurrences of a template image within a given screen image.

            Args:
                temp (str): The file path of the template image.
                pos (str, optional): The position of the found occurrences. Can be 'center' or 'bottom'. Defaults to 'center'.
                p1 (tuple, optional): The top-left coordinates of the region of interest. Defaults to (0, 0).
                p2 (tuple, optional): The bottom-right coordinates of the region of interest. Defaults to (0, 0).
                screen (numpy.ndarray, optional): The screen image. If not provided, the current screen image will be used. Defaults to None.
                threshold (float, optional): The threshold value for template matching. Defaults to 0.8.

            Returns:
                list: A list of dictionaries, each containing the coordinates of a found occurrence.
            """
        template = self.load_image(temp)
        screen_gray = screen
        if screen is None:
            screen_gray = self.get_screen_gray()
        x1, y1 = p1
        x2, y2 = p2
        w, h = template.shape[::-1]
        screen_w, screen_h = screen_gray.shape[::-1]
        if x2 == 0:
            x2 = screen_w
        if y2 == 0:
            y2 = screen_h
        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)

        (y_points, x_points) = np.where(res >= threshold)

        rects = []
        for (x, y) in zip(x_points, y_points):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if pos == 'center':
                    x = x + int(w / 2)
                    y = y + int(h / 2)

                if pos == 'bottom':
                    x = x + int(w / 2)
                    y = y + int(h / 2)
                rects.append((x, y, x + w, y + h))

        rects = non_max_suppression(np.array(rects))
        result = []
        for (x, y, x1, y1) in rects:
            result.append(dict(x=x, y=y, x1=x1, y1=y1))
        return result

    def get_screen_gray(self, bgr=False, crop=False, crop_pos=(0, 0, 100, 100)):
        """
            Get the grayscale version of the screen.

            Args:
                bgr (bool, optional): Whether to return the image in BGR format. Defaults to False.
                crop (bool, optional): Whether to crop the screen image. Defaults to False.
                crop_pos (tuple, optional): The position to crop the screen image. Defaults to (0, 0, 100, 100).

            Returns:
                numpy.ndarray: The grayscale screen image.
            """
        screen = self.d.screenshot()  # pil image
        if crop:
            screen = screen.crop(crop_pos)
            return screen

        screen = np.array(screen)
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        if not bgr:
            screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        # screen_gray = self.resize(screen_gray)
        return screen_gray

    @staticmethod
    def resize(img):
        """
        Resize the input image to a specified width while maintaining the aspect ratio.

        Parameters:
        img (numpy.ndarray): The input image to be resized.

        Returns:
        numpy.ndarray: The resized image.
        """
        width = img.shape[1]
        height = img.shape[0]
        w = 960
        scale_percent = w / width  # percent of original size

        dim = (int(width * scale_percent), int(height * scale_percent))

        # resize image
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        return resized

    def back(self, click=False, btn_back=None):
        """
        Simulates the back button press on an Android device.

        Args:
            click (bool, optional): If True, the back button is clicked instead of using the keyevent. Defaults to False.
            btn_back (dict, optional): The coordinates of the back button on the screen. Required if click is True.

        Returns:
            None
        """
        if not click:
            self.d.shell('input keyevent 4')
        else:
            self.d.click(btn_back['x'], btn_back['y'])
        sleep(1)

    def find_and_click(self, temp, pos='center', p=(0, 0), number=1, sort='y', screen=None, index=0,
                       threshold=0.8, long_press=False, delta=(0, 0)):
        """
            Finds the specified template on the screen and clicks on it.

            Args:
                temp (str): The path to the template image.
                pos (str, optional): The position of the template to click. Defaults to 'center'.
                p (tuple, optional): The starting point to search for the template. Defaults to (0, 0).
                number (int, optional): The number of times to click on the template. Defaults to 1.
                sort (str, optional): The sorting order of the found templates. Defaults to 'y'.
                screen (str, optional): The path to the screen image. Defaults to None.
                index (int, optional): The index of the template to click. Defaults to 0.
                threshold (float, optional): The threshold value for template matching. Defaults to 0.8.
                long_press (bool, optional): Whether to perform a long press instead of a regular click. Defaults to False.
                delta (tuple, optional): delta value x and y from template points
            Returns:
                bool: True if the template was found and clicked, False otherwise.
            """
        (x1, y1) = p
        points = self.find_by_template(temp=temp, pos=pos, p1=(x1, y1), screen=screen,
                                       threshold=threshold)
        points = sorted(points, key=lambda d: d[sort], reverse=False)
        if len(points) > 0:
            self.fail = 0
            if points[index] is not None:
                x = points[index]["x"]
                y = points[index]["y"]
            else:
                x = points[index]["x"]
                y = points[index]["y"]
            if long_press:
                self.long_press(x + delta[0], y + delta[1])
            else:
                for i in range(number):
                    self.d.click(x + delta[0], y + delta[1])
                    # print(f'clicked: {temp}: ({x}, {y})')
                    sleep(0.1)

            sleep(1)
            return True
        else:
            return False

    def find_and_hold(self, temp, pos='center', p=(0, 0)):
        """
        Finds the specified template on the screen and holds it by performing a swipe gesture.

        Args:
            temp (str): The path to the template image file.
            pos (str, optional): The position of the template to be found. Defaults to 'center'.
            p (tuple, optional): The starting position of the swipe gesture. Defaults to (0, 0).
        """
        (x1, y1) = p
        points = self.find_by_template(temp=temp, pos=pos, p1=(x1, y1))

        if len(points) > 0:
            x = points[0]["x"]
            y = points[0]["y"]
            x1 = x + 1
            y1 = y + 1
            self.d.shell(f'input swipe {x} {y} {x1} {y1} 10000')
            # input swipe [xcoord] [ycoord] [xcoord] [ycoord] 1000
            sleep(1)
        else:
            print(f'cannot find {temp}')

    def check_screen(self, temp, screen=None, threshold=0.8):
        """
        Check if the given template appears on the screen.

        Args:
            temp (str): The path to the template image file.
            screen (str, optional): The path to the screen image file. If not provided, the current screen will be used.
            threshold (float, optional): The matching threshold. Defaults to 0.8.

        Returns:
            bool: True if the template is found on the screen, False otherwise.
        """
        points = self.find_by_template(temp, screen=screen, threshold=threshold)
        if len(points) > 0:
            return True
        return False

    def kill_app(self):
        """
        Stops the execution of the app.
        """
        self.d.app_stop(self.app_package)

    def check_app_is_running(self):
        """
        Check if the app is running by checking its process ID (PID).

        Returns:
            bool: True if the app is running, False otherwise.
        """
        pid = self.d.shell(f'pidof {self.app_package}')
        if not pid:
            return False
        return True

    def long_press(self, x, y):
        """
        Perform a long press action at the specified coordinates (x, y).

        Args:
            x (int): The x-coordinate of the press location.
            y (int): The y-coordinate of the press location.
        """
        self.d.swipe(x, y, x, y, 5)

    def swipe(self, start=None, end=None, threshold=0.5):
        self.d.swipe(start[0], start[1], end[0], end[1], threshold)

    def enter_text(self, text):
        self.d.shell(f'input text {text}')