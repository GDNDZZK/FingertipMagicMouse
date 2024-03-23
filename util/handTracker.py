import cv2
import mediapipe as mp
from threading import Thread, Event
import numpy as np


class HandTracker:
    def __init__(self, callback=None, title='FingertipMagicMouse'):
        self.callback = callback
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75
        )
        self.cap = cv2.VideoCapture(0)
        self.thread = None
        self.running = Event()
        self.window_visible = True
        self.text = ''
        self.title = title

    def _process_frame(self):
        while self.running.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame_height, frame_width, _ = frame.shape
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
                        cv2.putText(frame, f"{idx+1}" if not idx + 1 == 1 else f"{idx+1} Type: {hand_info['type']}", (
                            x_pixel, y_pixel-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, self.text, (10, frame_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(self.title, frame)

            if cv2.waitKey(1) & 0xFF == 27:
                self.stop()

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

    def show_text(self, text):
        self.text = text

    def stop(self):
        self.running.clear()
        self.cap.release()
        cv2.destroyAllWindows()
