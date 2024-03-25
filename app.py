import tkinter as tk
from PIL import ImageGrab
from util.handTracker import HandTracker


def press(d):
    if not d:
        return
    # 要判断的手
    hand = "Right"
    # 获取坐标点
    hand_point = [i for i in d if i['type'] == hand]
    if not hand_point:
        return
    hand_point = hand_point[0]
    # 食指是否抬起
    index_finger = hand_point[9][1] <= hand_point[8][1] <= hand_point[7][1] <= hand_point[6][1]
    # 中指是否抬起
    middle_finger = hand_point[13][1] <= hand_point[12][1] <= hand_point[11][1] <= hand_point[10][1]
    # 无名指是否抬起
    medical_finger = hand_point[17][1] <= hand_point[16][1] <= hand_point[15][1] <= hand_point[14][1]
    # TODO 计算移动范围,比例


def get_screen_resolution():
    """获取屏幕真实分辨率(不受缩放倍率影响)"""
    # 截图
    screen = ImageGrab.grab()
    # 通过截图得到屏幕分辨率
    w, h = screen.size
    return w, h


def get_screen_resolution_tkinter():
    """获取屏幕分辨率(受缩放倍率影响)"""
    # 创建窗口
    tk_root = tk.Tk()
    # 通过窗口大小得到分辨率
    w = tk_root.winfo_screenwidth()
    h = tk_root.winfo_screenheight()
    # 关闭窗口
    tk_root.destroy()
    return w, h


def calculate_simplified_ratio(num1, num2):
    """
    计算两个数字的简化比例。

    Args:
    num1 (int): 第一个数字
    num2 (int): 第二个数字

    Return:
    ratio_numerator (int): 简化比例的分子
    ratio_denominator (int): 简化比例的分母
    """
    def gcd(a, b):
        """
        计算最大公约数。

        Args:
        a (int): 第一个整数
        b (int): 第二个整数

        Return:
        int: 两个整数的最大公约数。
        """
        while b:
            a, b = b, a % b
        return a

    common_divisor = gcd(num1, num2)
    ratio_numerator = num1 // common_divisor
    ratio_denominator = num2 // common_divisor

    return ratio_numerator, ratio_denominator


def max_cropped_size(length, width, ratio_length, ratio_width):
    """
    根据给定的宽高比计算裁剪后的矩形的最大尺寸。

    Args:
    length (int): 原始矩形的长度。
    width (int): 原始矩形的宽度。
    ratio_length (int): 裁剪目标的长度。
    ratio_width (int): 裁剪目标的宽度。

    Return:
    cropped_length (int): 裁剪后的矩形的长度。
    cropped_width (int): 裁剪后的矩形的宽度。
    """
    # 计算宽高比
    original_ratio = length / width
    target_ratio = ratio_length / ratio_width

    # 检查原始矩形是否已经符合宽高比
    if original_ratio <= target_ratio:
        # 如果原始矩形比目标比例更高，则裁剪宽度
        cropped_width = length / target_ratio
        if cropped_width <= width:
            return length, cropped_width
        else:
            # 如果裁剪后的宽度超过原始宽度，则改为裁剪长度
            cropped_length = width * target_ratio
            return cropped_length, width
    else:
        # 如果原始矩形比目标比例更宽，则裁剪长度
        cropped_length = width * target_ratio
        if cropped_length <= length:
            return cropped_length, width
        else:
            # 如果裁剪后的长度超过原始长度，则改为裁剪宽度
            cropped_width = length / target_ratio
            return length, cropped_width


def get_rectangle_coordinates(large_length, large_width, small_length, small_width):
    """
    计算较小矩形在较大矩形中居中放置时的坐标。

    Args:
    large_length (int): 较大矩形的长度。
    large_width (int): 较大矩形的宽度。
    small_length (int): 较小矩形的长度。
    small_width (int): 较小矩形的宽度。

    Returns:
    tuple: 包含较小矩形的左上角坐标和右下角坐标的元组。
    """

    # 计算较小矩形的左上角坐标
    top_left_x = (large_length - small_length) // 2
    top_left_y = (large_width - small_width) // 2

    # 计算较小矩形的右下角坐标
    bottom_right_x = top_left_x + small_length
    bottom_right_y = top_left_y + small_width

    # 返回左上角和右下角的坐标
    return (top_left_x, top_left_y), (bottom_right_x, bottom_right_y)


def main():
    # 获取屏幕分辨率
    screen_width, screen_height = get_screen_resolution()
    print(screen_width, screen_height)
    proportion_width, proportion_height = calculate_simplified_ratio(screen_width, screen_height)
    print(proportion_width, proportion_height)
    # 手部识别
    ht = HandTracker(press, camera_id=1, horizontal_flip=True)
    ht.start()
    ht.set_text('test')
    # 计算判定范围(相机范围中等比例裁切到屏幕比例)
    camera_width, camera_height = ht.get_camera_size()
    print(camera_width, camera_height)
    # 边框:
    # 裁剪后的长宽
    ratio_width, ratio_height = max_cropped_size(camera_width, camera_height, proportion_width, proportion_height)
    # 缩放
    t = 0.8
    ratio_width *= t
    ratio_height *= t
    print(ratio_width, ratio_height)
    p1, p2 = get_rectangle_coordinates(camera_width, camera_height, ratio_width, ratio_height)
    # 如果宽更小
    thickness = 1
    ht.show_frame(p1[0], p1[1], p2[0] - thickness, p2[1], thickness=thickness)
    # ht.show_frame(10, 20, 30, 40)


if __name__ == '__main__':
    main()
    # print(max_cropped_size(640, 480, 16, 9))
