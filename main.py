import sys
import os
import cv2
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import google.generativeai as genai

# Configure Gemini API key
GOOGLE_API_KEY = "AIzaSyB3SvfNCUdCX9wbrjFJQddWbSqgLT86S0"
genai.configure(api_key=GOOGLE_API_KEY)

# Ensure working directory is script folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Prompt for image analysis
def analyze_with_gemini(image_bytes, prompt=(
    "너는 IT 기기에 익숙하지 않은 사람을 돕는 안내 도우미야. "
    "사용자는 키오스크 화면을 사진으로 캡처해서 너에게 보여줄 거야. "
    "너는 이 이미지를 보고 사용자가 어떤 버튼을 누를 건지 하나의 질문을 해줘. "
    "만약 사용자가 눌러야 할 버튼이 하나뿐이라면 질문 대신 가이드를 해주고, 그 가이드 앞 뒤에 '/'를 달아줘."
    "다만 이때 주어진 이미지에 대해서만 분석하고 절대 다음 상태를 예상, 예측하지마."
    "너 사용자에게 한 질문 앞 뒤에 '*'을 달아줘. "
    "절대로 이 규칙을 잊지 마."
)):
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    response = model.generate_content(
        [prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}]
    )
    return response.text.strip()

class AnalyseAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("analyse_a.ui", self)
        self.pushButton_2.clicked.connect(self.open_analyze_b)
        self.pushButton_3.clicked.connect(self.open_camera)
        self.pushButton_4.clicked.connect(self.open_home)

    def open_analyze_b(self, result_text=None):
        self.hide()
        self.analyze_b_window = AnalyzeBWindow(result_text)
        self.analyze_b_window.show()

    def open_camera(self):
        self.hide()
        self.camera_window = CameraScreenWindow()
        self.camera_window.show()

    def open_home(self):
        self.hide()
        self.home_window = HomeWindow()
        self.home_window.show()

class AnalyzeBWindow(QMainWindow):
    def __init__(self, received_text):
        super().__init__()
        uic.loadUi("analyze_b.ui", self)
        self.messageLabel.setText(str(received_text))
        self.screen_but.clicked.connect(self.open_analyse_a)
        self.back_but.clicked.connect(self.open_home)
        self.reshot_but.clicked.connect(self.open_camera)

    def open_analyse_a(self):
        self.hide()
        self.analyse_a_window = AnalyseAWindow()
        self.analyse_a_window.show()

    def open_home(self):
        self.hide()
        self.home_window = HomeWindow()
        self.home_window.show()

    def open_camera(self):
        self.hide()
        self.camera_window = CameraScreenWindow()
        self.camera_window.show()

class FinishWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("finish.ui", self)
        self.yes_but.clicked.connect(self.close)
        self.no_but.clicked.connect(self.open_home)

    def open_home(self):
        self.hide()
        self.home_window = HomeWindow()
        self.home_window.show()

class HelpWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("help.ui", self)
        self.back_but.clicked.connect(self.open_home)

    def open_home(self):
        self.hide()
        self.home_window = HomeWindow()
        self.home_window.show()

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("home.ui", self)
        self.exit_but.clicked.connect(self.open_finish)
        self.help_but.clicked.connect(self.open_help)
        self.pushButton_3.clicked.connect(self.open_camera)

    def open_finish(self):
        self.hide()
        self.finish_window = FinishWindow()
        self.finish_window.show()

    def open_help(self):
        self.hide()
        self.help_window = HelpWindow()
        self.help_window.show()

    def open_camera(self):
        self.hide()
        self.camera_window = CameraScreenWindow()
        self.camera_window.show()

class CameraScreenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("camera_screen.ui", self)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)
        self.current_frame = frame

        # Connect shot button here to ensure single binding
        self.shot_but.clicked.disconnect()
        self.shot_but.clicked.connect(self.capture_and_analyze)

    def capture_and_analyze(self):
        # Show loading
        self.loading_window = LoadingWindow(self)
        self.loading_window.show()
        # Encode image
        _, buffer = cv2.imencode('.jpg', self.current_frame)
        image_bytes = buffer.tobytes()
        # Analyze
        result = analyze_with_gemini(image_bytes)
        self.loading_window.close()
        # Show result window
        self.hide()
        self.analyze_b_window = AnalyzeBWindow(result)
        self.analyze_b_window.show()

class LoadingWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("loading.ui", self)
        self.reshot_but.clicked.connect(self.retry)

    def retry(self):
        self.close()
        if self.parent():
            self.parent().show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home = HomeWindow()
    home.show()
    sys.exit(app.exec_())
