import cv2
import mediapipe as mp
import math
import sys
from src.scripts.imports import *

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils


class PoseDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('ui/Main Logos/MPRUN_icon.png'))
        self.setWindowTitle('Trick Trainer')
        self.setFixedSize(800, 600)
        self.setLayout(QVBoxLayout())

        self.createUI()

    def createUI(self):
        # Create a QLabel to display the video feed
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.label)

        # Initialize webcam capture
        self.cap = cv2.VideoCapture(0)

        # Set up a timer to update the video feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(20)  # Update every 20 ms

    def updateFrame(self):
        success, frame = self.cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            return

        # Convert the frame to RGB as mediapipe requires this format
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image to detect pose
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            # Draw pose landmarks on the frame
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

        # Convert the frame to QImage and display it in the QLabel
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
