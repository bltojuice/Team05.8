import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from google import generativeai as genai

# Gemini API 초기화
genai.configure(api_key="AIzaSyB3SvfNCUQdCX9wbrjFJQddWbSqgLT86S0")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("카메라 축소 화면 출력")

        # 원하는 축소 크기 (예: 640x480)
        self.display_width = 1000
        self.display_height = 600
        self.resize(self.display_width, self.display_height + 50)
        self.center_window()

        # 카메라 시작
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("카메라를 열 수 없습니다.")

        # QLabel 설정
        self.label = QLabel(self)
        self.label.setFixedSize(self.display_width, self.display_height)

        # 종료 버튼
        self.close_button = QPushButton("종료", self)
        self.close_button.clicked.connect(self.close_app)

        # 레이아웃
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def center_window(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 축소 처리
            resized_frame = cv2.resize(frame, (self.display_width, self.display_height), interpolation=cv2.INTER_AREA)
            h, w, ch = resized_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(resized_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(q_img))

    def close_app(self):
        self.cap.release()
        self.timer.stop()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
