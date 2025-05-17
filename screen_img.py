import sys, os, cv2
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyB3SvfNCUQdCX9wbrjFJQddWbSqgLT86S0"
genai.configure(api_key=GOOGLE_API_KEY)

end = 0
pix = 0

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
    end = 1
    return response.text.strip()


# ① 작업 디렉터리 이동
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ② .ui 파일로부터 UiClass, QtBase 얻기
UiClass, QtBase = uic.loadUiType("camera_screen.ui")

class MyWindow(QtBase, UiClass):
    def __init__(self):
        super().__init__()
        # ③ setupUi 호출
        self.setupUi(self)

        # 예: QTimer 로 프레임 갱신
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.imageLabel.setPixmap(pix)
        self.imageLabel.setScaledContents(True)
        self.shot_but.clicked.connect(self.btn_clicked)

    def show_next(self):
        # next.ui 를 로드해서 새로운 QWidget 으로 만듭니다
        next_widget = uic.loadUi("loading.ui")
        # QMainWindow 의 중앙 위젯을 새로 교체
        self.setCentralWidget(next_widget)
        # ※ 이후 next.ui 안 위젯들은 next_widget.xxx 형태로 접근 가능

    # 슬롯은 동기 함수로 유지
    def btn_clicked(self):
        # async/await 대신 동기 호출
        self.last()

    # async 키워드 제거
    def last(self):
        # 만약 pix, end 를 전역변수로 쓰실 거면 아래 한 줄 추가
        global pix, end
    
        # 다음 화면 보여주기
        self.show_next()

        # 이미지 분석 결과 받아오기
        result = analyze_with_gemini(pix)

        # end 플래그가 1이 될 때까지 대기
        while end != 1:
            pass

        # 새 스크립트로 프로세스 교체
        os.execvp(sys.executable, [sys.executable, "screen_ana_b.py", str(result)])



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())


