# -*- encoding: utf-8 -*-
from pynput.mouse import Button, Controller


class MouseController:
    """鼠标控制类，包含鼠标的常用操作方法"""

    def __init__(self):
        """初始化鼠标控制器"""
        self.left_button_flag = False
        self.right_button_flag = False
        self.middle_button_flag = False
        self.mouse = Controller()

    def getPosition(self):
        """
        获取鼠标指针的当前坐标

        Returns:
        - x,y
        """
        return self.mouse.position

    def setPosition(self, x, y):
        """
        设置鼠标指针的坐标位置

        Args:
        - x: 横坐标
        - y: 纵坐标
        """
        self.mouse.position = (x, y)

    def mouseUp(self, mouse_move_speed=1):
        """鼠标向上移动"""
        x, y = self.getPosition()
        self.setPosition(x, y-mouse_move_speed)

    def mouseDown(self, mouse_move_speed=1):
        """鼠标向下移动"""
        x, y = self.getPosition()
        self.setPosition(x, y+mouse_move_speed)

    def mouseLeft(self, mouse_move_speed=1):
        """鼠标向左移动"""
        x, y = self.getPosition()
        self.setPosition(x-mouse_move_speed, y)

    def mouseRight(self, mouse_move_speed=1):
        """鼠标向右移动"""
        x, y = self.getPosition()
        self.setPosition(x+mouse_move_speed, y)

    def pressLeftButton(self):
        """鼠标左键按下"""
        if not self.left_button_flag:
            self.mouse.press(Button.left)
            self.left_button_flag = True

    def releaseLeftButton(self):
        """鼠标左键抬起"""
        if self.left_button_flag:
            self.mouse.release(Button.left)
            self.left_button_flag = False

    def pressRightButton(self):
        """鼠标右键按下"""
        if not self.right_button_flag:
            self.mouse.press(Button.right)
            self.right_button_flag = True

    def releaseRightButton(self):
        """鼠标右键抬起"""
        if self.right_button_flag:
            self.mouse.release(Button.right)
            self.right_button_flag = False

    def pressMiddleButton(self):
        """鼠标中键按下"""
        if not self.middle_button_flag:
            self.mouse.press(Button.middle)
            self.middle_button_flag = True

    def releaseMiddleButton(self):
        """鼠标中键抬起"""
        if self.middle_button_flag:
            self.mouse.release(Button.middle)
            self.middle_button_flag = False

    def scroll(self, x, y):
        """鼠标滚轮滚动"""
        self.mouse.scroll(x, y)

    def scrollUp(self, mouse_scroll_speed=3):
        """鼠标滚轮向上滚动"""
        self.scroll(0, mouse_scroll_speed)

    def scrollDown(self, mouse_scroll_speed=3):
        """鼠标滚轮向下滚动"""
        self.scroll(0, -1 * mouse_scroll_speed)

    def scrollLeft(self, mouse_scroll_speed=3):
        """鼠标滚轮向左滚动"""
        self.scroll(-1 * mouse_scroll_speed, 0)

    def scrollRight(self, mouse_scroll_speed=3):
        """鼠标滚轮向右滚动"""
        self.scroll(mouse_scroll_speed, 0)