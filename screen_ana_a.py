import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import os
import base64  # base64 decoding을 위해 추가

# ① 작업 디렉터리를 스크립트가 있는 곳으로 맞춰 주면
#    다른 디렉터리에서 실행해도 파일 이름만으로 찾습니다.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

form_class = uic.loadUiType("analyse_a.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.btn2_clicked)
        self.pushButton_3.clicked.connect(self.btn3_clicked)
        self.pushButton_4.clicked.connect(self.btn4_clicked)

        # screen_ana_b.py로부터 전달받은 데이터 처리
        self.received_text = ""
        self.received_image = ""
        if len(sys.argv) > 1:
            self.received_text = sys.argv[1]
            print(f"screen_ana_a.py: 받은 텍스트 데이터: {self.received_text}")
        if len(sys.argv) > 2:
            self.received_image = sys.argv[2]
            print(f"screen_ana_a.py: 받은 이미지 데이터: {self.received_image}")

    def btn2_clicked(self):
        self.close()
        args = [
            sys.executable,
            "screen_ana_b.py"
        ]
        if self.received_text:
            args.append(self.received_text)
        if self.received_image:
            args.append(self.received_image)
        os.execvp(sys.executable, args)

    def btn3_clicked(self):
        self.close()
        os.execvp(sys.executable, [sys.executable, "screen_img.py"])

    def btn4_clicked(self):
        self.close()
        os.execvp(sys.executable, [sys.executable, "screen_home.py"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()