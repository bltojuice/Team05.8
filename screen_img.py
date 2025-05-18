import sys
import os
import cv2
import base64
from io import BytesIO
from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from google import generativeai as genai
import time

# --- 더 이상 genai.configure는 사용하지 않습니다 ---

def encode_to_base64(s: str) -> str:
    """
    문자열을 UTF-8로 인코딩하고, Base64로 인코딩한 후 ASCII 문자열로 반환합니다.
    """
    # 문자열 → 바이트 변환(UTF-8)
    byte_data = s.encode('utf-8')
    # Base64 인코딩 → 바이트
    b64_bytes = base64.b64encode(byte_data)
    # 바이트 → 문자열
    return b64_bytes.decode('ascii')

GOOGLE_API_KEY = "AIzaSyB3SvfNCUQdCX9wbrjFJQddWbSqgLT86S0"  # 실제 API 키로 변경

# API 키를 전역적으로 설정합니다.
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_with_gemini(image_bytes: bytes, prompt: str = (
    "너는 IT 기기에 익숙하지 않은 사람을 돕는 안내 도우미야. "
    "사용자는 키오스크 화면 등 익숙하지 않은 상황의 사진으로 캡처해서 너에게 보여줄 거야. 다만 꼭 키오스크라는 보장은 없어. 다양한 상황에서 너를 사용할 거야."
    "너는 이 이미지를 보고 사용자가 어떻게 사용하거나 행동해야 하는지 자세히 알려줘"
    "이 입력에 대한 대답은 하지 않아도 되. 사용자가 어떻게 사용하거나 행동해야 하는지만 출력해"
    "또한, 약 30자마다 엔터를 쳐서 출력해. 사용자가 볼 화면에서 글자가 너무 길면 짤리기 때문이야."
    "키오스크가 아닐 수 있으니 꼭 키오스크 화면이 들어오리란 편견은 가지지 마."
)) -> str:
    """
    Gemini Pro Vision 모델을 사용하여 이미지 분석을 수행하고, 분석 결과를 문자열로 반환합니다.
    """
    # API 키는 configure에서 설정하므로 여기서는 전달하지 않습니다.
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    try:
        response = model.generate_content(
            [prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}]
        )
        for part in response.candidates[0].content.parts:
            if part.text:
                return part.text.strip()
        return "Gemini 응답에서 텍스트를 찾을 수 없습니다."
    except Exception as e:
        return f"Gemini 분석 오류: {e}"

def generate_image(image_bytes: bytes, prompt: str = (
    "이 이미지를 바탕으로 사용자 옆에 라마를 추가해줘"
), max_retries: int = 3, retry_delay: int = 2) -> bytes:
    """
    Gemini Pro Vision 모델을 사용하여 이미지를 생성하고, 생성된 이미지의 바이트 데이터를 반환합니다.
    이미지 생성에 실패하는 경우, 재시도 로직을 추가했습니다.
    """
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                [prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}]
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return base64.b64decode(part.inline_data.data)  # 바이트 데이터 반환
            print("이미지 생성 실패: Gemini 응답에서 이미지 데이터를 찾을 수 없습니다.")
            if attempt < max_retries - 1:
                print(f"재시도 ({attempt + 1}/{max_retries})...")
                time.sleep(retry_delay)  # 재시도 전에 잠시 대기
        except Exception as e:
            print(f"이미지 생성 오류 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"재시도 ({attempt + 1}/{max_retries})...")
                time.sleep(retry_delay)  # 재시도 전에 잠시 대기

    print("최대 재시도 횟수를 초과했습니다. 기본 이미지를 반환합니다.")
    # 기본 이미지를 반환하거나, 오류를 명확히 나타내는 바이트 데이터를 반환합니다.
    # 여기서는 간단히 빈 바이트를 반환하도록 하겠습니다. 필요에 따라 수정하세요.
    return b""

# ① 작업 디렉터리 이동
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ② .ui 파일로부터 UiClass, QtBase 얻기
UiClass, QtBase = uic.loadUiType("camera_screen.ui")

class MyWindow(QtBase, UiClass):
    """
    카메라 화면을 표시하고, 캡처된 이미지를 분석하고, 결과를 표시하는 메인 윈도우 클래스입니다.
    """
    def __init__(self):
        super().__init__()
        # ③ setupUi 호출
        self.setupUi(self)

        # QTimer를 사용하여 카메라 프레임을 주기적으로 갱신합니다.
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # '캡처' 버튼 클릭 시 last 함수를 호출합니다.
        self.shot_but.clicked.connect(self.last)

        self.latest_image_bytes = None  # 가장 최근에 캡처된 이미지 바이트를 저장합니다.

    def update_frame(self):
        """
        카메라에서 프레임을 읽어 QLabel에 표시하고,
        JPEG 바이트로 인코딩하여 self.latest_image_bytes에 저장합니다.
        """
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)
        success, buf = cv2.imencode('.jpg', frame)
        if success:
            self.latest_image_bytes = buf.tobytes()  # 이미지 바이트 저장

    def show_next(self):
        """
        loading.ui를 로드하여 로딩 화면을 표시합니다.
        """
        # next.ui 를 로드해서 새로운 QWidget 으로 만듭니다
        next_widget = uic.loadUi("loading.ui")
        # QMainWindow 의 중앙 위젯을 새로 교체
        self.setCentralWidget(next_widget)
        # ※ 이후 next.ui 안 위젯들은 next_widget.xxx 형태로 접근 가능

    def btn_clicked(self):
        """
        '분석' 버튼 클릭 시 호출됩니다. (현재 사용되지 않음)
        """
        # async/await 대신 동기 호출
        self.last()

    def last(self):
        """
        '캡처' 버튼 클릭 시 호출되어 이미지 분석 및 생성을 수행하고,
        결과를 다음 스크립트로 전달합니다.
        """
        if not self.latest_image_bytes:
            print("오류: 이미지 데이터가 없습니다.")
            return

        # 다음 화면 보여주기 (로딩 화면)
        self.show_next()

        # 이미지 분석 및 생성
        result_text = analyze_with_gemini(self.latest_image_bytes)
        generated_image_bytes = generate_image(self.latest_image_bytes)

        # 새 스크립트로 프로세스 교체
        encoded_text = encode_to_base64(result_text)
        encoded_image = base64.b64encode(generated_image_bytes).decode('ascii') if generated_image_bytes else ""

        print(f"screen_img.py: analyze_with_gemini 결과: {result_text}")
        print(f"screen_img.py: generate_image 결과 (길이): {len(generated_image_bytes)}")
        print(f"screen_img.py: os.execvp 호출, encoded_text 길이: {len(encoded_text)}, encoded_image 길이: {len(encoded_image)}")

        args = [
            sys.executable,
            "screen_ana_b.py",
            encoded_text,
            encoded_image
        ]
        print(f"screen_img.py: os.execvp에 전달하는 args: {args}")
        os.execvp(sys.executable, args)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())