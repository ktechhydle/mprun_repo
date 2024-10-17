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
        self.setWindowTitle('Trick Analyzer')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(800, 600)
        self.setLayout(QVBoxLayout())

        self.is_recording = False
        self.recorded_frames = []  # List to store recorded pose landmarks

        self.createUI()

    def createUI(self):
        # Create a QLabel to display the video feed
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.label)

        # Create buttons for recording and playing back
        btn_layout = QHBoxLayout()

        self.record_btn = QPushButton('Record', self)
        self.record_btn.clicked.connect(self.toggleRecording)
        btn_layout.addWidget(self.record_btn)

        self.play_btn = QPushButton('Play', self)
        self.play_btn.clicked.connect(self.playRecording)
        btn_layout.addWidget(self.play_btn)

        self.layout().addLayout(btn_layout)

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

            # If recording, store the pose landmarks
            if self.is_recording:
                self.recorded_frames.append(results.pose_landmarks)

        # Convert the frame to QImage and display it in the QLabel
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(q_image))

    def toggleRecording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_btn.setText('Record')
            print("Recording stopped.")
        else:
            self.recorded_frames = []  # Clear previous recordings
            self.is_recording = True
            self.record_btn.setText('Stop Recording')
            print("Recording started.")

    def playRecording(self):
        if not self.recorded_frames:
            print("No recording to play.")
            return

        # Stop any previously running playback timer
        if hasattr(self, 'playback_timer') and self.playback_timer.isActive():
            self.playback_timer.stop()

        print("Playing recorded animation...")
        self.timer.stop()

        self.current_frame = 0

        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.displayNextFrame)
        self.playback_timer.start(20)

    def displayNextFrame(self):
        if self.current_frame >= len(self.recorded_frames):
            self.playback_timer.stop()
            self.timer.start(20)
            return

        # Render the current pose frame
        landmarks = self.recorded_frames[self.current_frame]
        frame = self.renderPoseFromLandmarks(landmarks)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(q_image))

        # Move to the next frame
        self.current_frame += 1

    @staticmethod
    def renderPoseFromLandmarks(landmarks):
        # Create a blank frame (white background)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 255

        # Draw pose landmarks on the blank frame
        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        return frame

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
