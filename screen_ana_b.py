import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import os
import base64
from io import BytesIO
from PIL import Image

# ① 작업 디렉터리를 스크립트가 있는 곳으로 맞춰 주면
#    다른 디렉터리에서 실행해도 파일 이름만으로 찾습니다.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

form_class = uic.loadUiType("analyze_b.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 인자 존재 여부 확인
        if len(sys.argv) > 1:
            encoded = sys.argv[1]
            received = base64.urlsafe_b64decode(encoded.encode('ascii')).decode('utf-8')
            self.messageLabel.setText(received)
        else:
            self.messageLabel.setText("텍스트 분석 결과가 없습니다.")

        if len(sys.argv) > 2:
            imgen_encoded = sys.argv[2]
            if imgen_encoded:
                try:
                    imgen_decoded = base64.urlsafe_b64decode(imgen_encoded.encode('ascii'))
                    image = Image.open(BytesIO(imgen_decoded))
                    # 이미지를 화면에 표시하거나 다른 작업 수행
                except Exception as e:
                    print(f"이미지 처리 오류: {e}")
            else:
                print("생성된 이미지가 없습니다.")
        else:
            print("생성된 이미지 인자가 없습니다.")

        self.screen_but.clicked.connect(self.scbtn_clicked)
        self.back_but.clicked.connect(self.babtn_clicked)
        self.reshot_but.clicked.connect(self.rebtn_clicked)

    def scbtn_clicked(self):
        self.close()
        args = [
            sys.executable,  # 파이썬 인터프리터 경로
            "screen_ana_a.py",  # 실행할 스크립트
        ]
        if len(sys.argv) > 1:
            args.append(sys.argv[1])  # encoded
        if len(sys.argv) > 2:
            args.append(sys.argv[2])  # imgen
        os.execvp(sys.executable, args)

    def babtn_clicked(self):
        self.close()
        os.execvp(sys.executable, [sys.executable, "screen_home.py"])

    def rebtn_clicked(self):
        self.close()
        os.execvp(sys.executable, [sys.executable, "screen_img.py"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()