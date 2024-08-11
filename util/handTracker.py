import cv2
import mediapipe as mp
from threading import Thread, Event
import numpy as np


class HandTracker:
    def __init__(self, callback=None, title='FingertipMagicMouse', camera_id=0, horizontal_flip=False, move_finger = '食指'):
        self.callback = callback
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75
        )
        self.cap = cv2.VideoCapture(camera_id)
        self.thread = None
        self.running = Event()
        self.window_visible = True
        self.text = ''
        self.text_rgb = (255, 255, 255)
        self.title = title
        self.horizontal_flip = horizontal_flip
        self.camera_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.camera_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.move_finger = move_finger

    def _process_frame(self):
        while self.running.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame_height, frame_width, _ = frame.shape
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.horizontal_flip:
                frame = cv2.flip(frame, 1)
            results = self.hands.process(frame)

            hand_data = []
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    hand_type = "Left" if handedness.classification[0].label == "Left" else "Right"
                    hand_points = {}
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        # Convert the normalized coordinates to pixel values
                        # 坐标比例转像素值
                        x_pixel = int(landmark.x * frame_width)
                        y_pixel = int(landmark.y * frame_height)
                        z = landmark.z
                        # Also include the normalized coordinates
                        # 同时包含归一化坐标
                        x_norm = landmark.x
                        y_norm = landmark.y
                        hand_points[idx+1] = [x_pixel, y_pixel, z, x_norm, y_norm]
                    hand_data.append({"type": hand_type, **hand_points})

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks and self.window_visible:
                for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, hand_data):
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                    # Display the type of hand at the bottom of each hand
                    # 显示type
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        x_pixel, y_pixel, z, x_norm, y_norm = hand_info[idx+1]
                        # cv2.putText(frame, f"{idx+1}:({x_pixel},{y_pixel},{z:.2f}) - ({x_norm:.2f},{y_norm:.2f})", (x_pixel, y_pixel-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        # cv2.putText(frame, f"{idx+1}" if not idx + 1 == 1 else f"{idx+1} Type: {hand_info['type']}", (x_pixel, y_pixel-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        if idx + 1 == 1:
                            cv2.putText(frame, f"{hand_info['type']}", (
                                x_pixel, y_pixel-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        elif idx+1 == 9 and self.move_finger == '食指':
                            cv2.putText(frame, '^', (
                                x_pixel - 11, y_pixel + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        elif idx+1 == 13 and self.move_finger == '中指':
                            cv2.putText(frame, '^', (
                                x_pixel - 11, y_pixel + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        elif idx+1 == 17 and self.move_finger == '无名指':
                            cv2.putText(frame, '^', (
                                x_pixel - 11, y_pixel + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        elif idx+1 == 21 and self.move_finger == '小拇指':
                            cv2.putText(frame, '^', (
                                x_pixel - 11, y_pixel + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # 显示文字
            cv2.putText(frame, self.text, (10, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_rgb, 2)
            # 绘制边框
            if self.frame_visible:
                cv2.rectangle(frame, (self.frame_x1, self.frame_y1), (self.frame_x2,
                              self.frame_y2), self.frame_color, self.frame_thickness)
            cv2.imshow(self.title, frame)
            cv2.waitKey(1)
            if self.callback:
                self.callback(hand_data)

    def start(self):
        if not self.thread or not self.thread.is_alive():
            self.running.set()
            self.thread = Thread(target=self._process_frame)
            self.thread.start()

    def hide_window(self):
        self.window_visible = False

    def show_window(self):
        self.window_visible = True

    def set_text(self, text, rgb=(255, 255, 255)):
        self.text_rgb = rgb
        self.text = text

    def set_title(self, title):
        self.title = title

    def get_camera_size(self):
        return int(self.camera_width), int(self.camera_height)

    def show_frame(self, x1, y1, x2, y2, color=(0, 255, 0), thickness=1):
        self.frame_x1 = int(x1)
        self.frame_y1 = int(y1)
        self.frame_x2 = int(x2)
        self.frame_y2 = int(y2)
        self.frame_color = color
        self.frame_thickness = thickness
        self.frame_visible = True

    def hide_frame(self):
        self.frame_visible = False

    def stop(self):
        self.running.clear()
        self.cap.release()
        cv2.destroyAllWindows()
