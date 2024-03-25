from util.handTracker import HandTracker
import tkinter as tk

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

def main():
    # 获取屏幕分辨率
    tki = tk.Tk()
    screen_width = tki.winfo_screenwidth()
    screen_height = tki.winfo_screenheight()
    tki.destroy()
    print(screen_width, screen_height)
    # 手部识别
    ht = HandTracker(press, camera_id=1, horizontal_flip=True)
    ht.start()
    ht.set_text('test')
    # TODO 计算移动范围
    ht.show_frame(10,10,50,50)


if __name__ == '__main__':
    main()
