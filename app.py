import json
from statistics import median
import time
import numpy as np
from filterpy.kalman import KalmanFilter
import os
import sys
import tkinter as tk
from PIL import ImageGrab
from util.SystemTrayIcon import SystemTrayIcon
from util.handTracker import HandTracker
from util.loadSetting import getConfigDict
from util.mouseController import MouseController


def convert_coordinate(x1, y1, p1):
    # 计算两个坐标系之间的比例因子
    scale_factor = 1 / (y1 - x1)

    # 计算坐标系2中的p2
    p2 = (p1 - x1) * scale_factor

    return p2


# 全局变量，用于存储卡尔曼滤波器实例
kf = None


def kalman_filter(current_x, current_y):
    """
    使用卡尔曼滤波计算当前坐标。

    :param sample_size: 采样数量，这里用于初始化卡尔曼滤波器。
    :param current_x: 当前x坐标。
    :param current_y: 当前y坐标。
    :return: 计算后的坐标元组。
    """

    global kf

    # 如果是第一次调用，初始化卡尔曼滤波器
    if kf is None:
        kf = KalmanFilter(dim_x=2, dim_z=2)
        kf.x = np.array([current_x, current_y])  # 初始状态
        kf.F = np.array([[1., 0.], [0., 1.]])    # 状态转移矩阵
        kf.H = np.array([[1., 0.], [0., 1.]])    # 观测矩阵
        kf.P *= 1000.                            # 状态估计协方差矩阵
        kf.R = np.array([[1., 0.], [0., 1.]])    # 观测噪声协方差矩阵
        kf.Q = np.array([[1., 0.], [0., 1.]])    # 过程噪声协方差矩阵

    # 进行卡尔曼滤波器的预测和更新步骤
    kf.predict()
    kf.update(np.array([current_x, current_y]))

    # 返回滤波后的坐标
    return kf.x[0], kf.x[1]


# 全局变量，用于存储历史坐标数据
history_filter_avg = []


def moving_average_filter(current_x, current_y):
    """使用移动平均法计算当前坐标"""
    global history_filter_avg, config
    sample_size = int(config['MOVE_SAMPLE_SIZE_AVG'])
    # 将当前坐标添加到历史列表中
    history_filter_avg.append((current_x, current_y))

    # 如果历史数据超过采样数量，则移除最早的数据
    if len(history_filter_avg) > sample_size:
        history_filter_avg.pop(0)

    # 计算所有历史坐标的平均值
    avg_x = sum([coord[0] for coord in history_filter_avg]) / len(history_filter_avg)
    avg_y = sum([coord[1] for coord in history_filter_avg]) / len(history_filter_avg)

    return avg_x, avg_y


# 全局变量，用于存储历史坐标数据
history_filter_median = []


def median_filter(current_x, current_y):
    """使用中值滤波计算当前坐标"""
    global history_filter_median, config
    # 将当前坐标添加到历史列表中
    sample_size = int(config['MOVE_SAMPLE_SIZE_MEDIAN'])
    history_filter_median.append((current_x, current_y))

    # 如果历史数据超过采样数量，则移除最早的数据
    if len(history_filter_median) > sample_size:
        history_filter_median.pop(0)

    # 分别计算x和y坐标的中值
    x_coords = [coord[0] for coord in history_filter_median]
    y_coords = [coord[1] for coord in history_filter_median]
    avg_x = median(x_coords)
    avg_y = median(y_coords)

    return avg_x, avg_y


last_coord = None


def threshold_filter(x, y):
    """使用阈值过滤法计算当前坐标"""
    global last_coord, config
    threshold = float(config['MOVE_THRESHOLD'])
    current_coord = (x, y)
    # 如果是第一次调用，或者上一次坐标为None，直接返回当前坐标
    if last_coord is None:
        last_coord = current_coord
        return current_coord[0], current_coord[1]

    # 计算两点之间的距离
    distance = ((current_coord[0] - last_coord[0]) ** 2 + (current_coord[1] - last_coord[1]) ** 2) ** 0.5
    # 如果距离大于阈值，则更新并返回当前坐标
    if distance > threshold:
        last_coord = current_coord
        return current_coord[0], current_coord[1]
    # 否则返回上次坐标
    else:
        return last_coord[0], last_coord[1]


def filter(x, y):
    """自动选取指定的方法计算当前坐标"""
    global move_filter
    if '禁用' in move_filter:
        return x, y
    if '卡尔曼滤波' in move_filter:
        x, y = kalman_filter(x, y)
    if '移动平均' in move_filter:
        x, y = moving_average_filter(x, y)
    if '中值滤波' in move_filter:
        x, y = median_filter(x, y)
    if '阈值过滤' in move_filter:
        x, y = threshold_filter(x, y)
    return x, y


temp_text = ''


def press(d):
    """处理每一帧传入的数据,判断与执行"""
    global now_distance, temp_text, left_fingers, right_fingers, middle_fingers, move_finger, left_click_finger, right_click_finger
    if not d:
        return
    # 要判断的手
    hand = config['HAND']
    # 获取坐标点
    hand_point = [i for i in d if i['type'].upper() == hand.upper()]
    if not hand_point:
        return
    hand_point = hand_point[0]
    # 设置当前距离
    now_distance = hand_point[9][2]
    # // *不准确* 大拇指是否抬起
    # // thumb =hand_point[5][1] <= hand_point[4][1] <= hand_point[3][1] <= hand_point[2][1]
    # 食指是否抬起
    index_finger = hand_point[9][1] <= hand_point[8][1] <= hand_point[7][1] <= hand_point[6][1]
    # 中指是否抬起
    middle_finger = hand_point[13][1] <= hand_point[12][1] <= hand_point[11][1] <= hand_point[10][1]
    # 无名指是否抬起
    medical_finger = hand_point[17][1] <= hand_point[16][1] <= hand_point[15][1] <= hand_point[14][1]
    # 小拇指是否抬起
    little_finger = hand_point[21][1] <= hand_point[20][1] <= hand_point[19][1] <= hand_point[18][1]
    # 设置手指集合
    finger_set = set()
    if index_finger:
        finger_set.add('食指')
    if middle_finger:
        finger_set.add('中指')
    if medical_finger:
        finger_set.add('无名指')
    if little_finger:
        finger_set.add('小拇指')
    # 计算移动范围,比例
    x_proportion = convert_coordinate(p1[2], p2[2], hand_point[9][3] if move_finger == '食指' else hand_point[13][3] if move_finger ==
                                      '中指' else hand_point[17][3] if move_finger == '无名指' else hand_point[21][3] if move_finger == '小拇指' else 0)
    y_proportion = convert_coordinate(p1[3], p2[3], hand_point[9][4] if move_finger == '食指' else hand_point[13][4] if move_finger ==
                                      '中指' else hand_point[17][4] if move_finger == '无名指' else hand_point[21][4] if move_finger == '小拇指' else 0)
    if x_proportion <= 0:
        x_proportion = 0
    elif x_proportion >= 1:
        x_proportion = 1
    if y_proportion <= 0:
        y_proportion = 0
    elif y_proportion >= 1:
        y_proportion = 1
    x = int(x_proportion * screen_width)
    y = int(y_proportion * screen_height)
    # 左键
    if left_fingers == finger_set:
        mouse_ctl.pressLeftButton()
        temp_text = 'L'
    elif left_click_finger == finger_set:
        if not temp_text == 'LC':
            mouse_ctl.pressLeftButton()
            temp_text = 'LC'
            time.sleep(0.01)
            mouse_ctl.releaseLeftButton()
    else:
        mouse_ctl.releaseLeftButton()
        if temp_text in ['L', 'LC']:
            temp_text = ''
    # 右键
    if right_fingers == finger_set:
        mouse_ctl.pressRightButton()
        temp_text = 'R'
    elif right_click_finger == finger_set:
        if not temp_text == 'RC':
            mouse_ctl.pressRightButton()
            temp_text = 'RC'
            time.sleep(0.01)
            mouse_ctl.releaseRightButton()
    else:
        mouse_ctl.releaseRightButton()
        if temp_text in ['R', 'RC']:
            temp_text = ''
    # 中键
    if middle_fingers == finger_set:
        mouse_ctl.pressMiddleButton()
        temp_text = 'M'
    else:
        mouse_ctl.releaseMiddleButton()
        if temp_text == 'M':
            temp_text = ''
    # TODO 滚轮
    # 移动鼠标(食指)
    if move_finger in finger_set:
        x, y = filter(x, y)
        mouse_ctl.setPosition(x, y)
        ht.set_text(f'{int(x)} {int(y)} {temp_text}')
    else:
        ht.set_text('')


def get_screen_resolution():
    """获取屏幕真实分辨率(不受系统缩放倍率影响)"""
    # 截图
    screen = ImageGrab.grab()
    # 通过截图得到屏幕分辨率
    w, h = screen.size
    return w, h


def get_screen_resolution_tkinter():
    """获取屏幕分辨率(受系统缩放倍率影响)"""
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
    return [top_left_x, top_left_y], [bottom_right_x, bottom_right_y]


def checkPath():
    """确保工作路径正确"""
    # 获取当前工作路径
    current_work_dir = os.getcwd()
    print_info(f"当前工作路径：{current_work_dir}")

    # 获取当前文件所在路径
    current_file_dir = os.path.dirname(__file__)
    print_info(f"文件所在路径：{current_file_dir}")
    # 如果文件所在路径末尾是(_internal),跳转到上一级
    if '_internal' == current_file_dir[-9:]:
        current_file_dir = current_file_dir[:-9]
        print_info('internal')
        print_info(f"文件所在路径：{current_file_dir}")

    # 如果工作路径不是文件所在路径，切换到文件所在路径
    if current_work_dir != current_file_dir:
        os.chdir(current_file_dir)
        print_info("已切换到文件所在路径。")


activation_flag = True
activation_key_is_press = False


def print_info(*args, end='\n', file=None, flush=False):
    """输出info级别的信息"""
    print("INFO:", *args, end=end, file=file, flush=flush)


def main():
    global config, screen_width, screen_height, ratio_width, ratio_height, p1, p2
    global ht, mouse_ctl, left_fingers, right_fingers, middle_fingers, move_finger, move_filter, left_click_finger, right_click_finger
    # 确保工作路径正确
    checkPath()
    # 获取设置
    config = getConfigDict()
    # 打印当前使用的滤波器
    print_info('滤波器:', config['MOVE_FILTER'])
    move_filter = config['MOVE_FILTER'].split('+')
    # 获取左键手指
    left_fingers = set(config['LEFT_FINGERS'].split('+'))
    left_click_finger = set(config['LEFT_CLICK_FINGER'].split('+'))
    # 获取右键手指
    right_fingers = set(config['RIGHT_FINGERS'].split('+'))
    right_click_finger = set(config['RIGHT_CLICK_FINGER'].split('+'))
    # 获取中键手指
    middle_fingers = set(config['MIDDLE_FINGERS'].split('+'))
    # 获取移动手指
    move_finger = config['MOVE_FINGER']
    # 鼠标控制器
    mouse_ctl = MouseController()
    # 获取屏幕分辨率
    screen_width, screen_height = get_screen_resolution()
    print_info('分辨率:', screen_width, screen_height)
    proportion_width, proportion_height = calculate_simplified_ratio(screen_width, screen_height)
    print_info('比例:', proportion_width, proportion_height)
    # 手部识别
    ht = HandTracker(press, camera_id=int(config['CAMERA_ID']),
                     horizontal_flip=config['HORIZONTAL_FLIP'].upper() == 'TRUE', move_finger=move_finger)
    ht.start()
    # 计算判定范围(相机范围中等比例裁切到屏幕比例)
    camera_width, camera_height = ht.get_camera_size()
    print_info('相机分辨率:', camera_width, camera_height)
    # 边框:
    # 裁剪后的长宽
    ratio_width, ratio_height = max_cropped_size(camera_width, camera_height, proportion_width, proportion_height)
    # 缩放
    t = float(config['ZOOM_MAGNIFICATION'])
    ratio_width *= t
    ratio_height *= t
    print_info('裁切后相机分辨率:', int(ratio_width), int(ratio_height))
    # 获取坐标
    p1, p2 = get_rectangle_coordinates(camera_width, camera_height, ratio_width, ratio_height)
    # 左边转比例
    p1.append(p1[0] / camera_width)
    p1.append(p1[1] / camera_height)
    p2.append(p2[0] / camera_width)
    p2.append(p2[1] / camera_height)
    # p1[2], p2[2] = p1[0] / camera_width, p2[0] / camera_width
    # p1[3], p2[3] = p1[1] / camera_height, p2[1] / camera_height
    # 如果宽更小
    thickness = 1
    ht.show_frame(p1[0], p1[1], p2[0] - thickness, p2[1], thickness=thickness)
    # print_info(convert_coordinate(p1[2], p2[2], p1[2]))
    # print_info(convert_coordinate(p1[2], p2[2], 0.5))
    # print_info(convert_coordinate(p1[2], p2[2], p2[2]))
    # ht.show_frame(10, 20, 30, 40)
    # 托盘图标
    sys_icon = SystemTrayIcon()
    # 开启图标,阻塞主线程
    sys_icon.start()
    # 图标关闭,退出程序
    ht.stop()
    sys.exit(0)


if __name__ == '__main__':
    main()
    # print_info(max_cropped_size(640, 480, 16, 9))
