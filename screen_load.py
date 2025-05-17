import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import os, sys

# ① 작업 디렉터리를 스크립트가 있는 곳으로 맞춰 주면
#    다른 디렉터리에서 실행해도 파일 이름만으로 찾습니다.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

form_class = uic.loadUiType("loading.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
 #       self.reshot_but.clicked.connect(self.btn_clicked)

    def btn_clicked(self):
        self.close()
        #os.execvp(sys.executable, [sys.executable, "other.py"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()