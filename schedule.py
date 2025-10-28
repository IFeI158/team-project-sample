import pymysql
import serial
from dbconnect import DB, config
from PyQt5.QtWidgets import *
import test

class Schedule(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowTitle("시간표 관리")

        central = QWidget()
        layout = QVBoxLayout(central)

        self.btn1 = QPushButton("시간표 조회")
        layout.addWidget(self.btn1)
        self.btn2 = QPushButton("시간표 추가")
        layout.addWidget(self.btn2)
        self.btn3 = QPushButton("시간표 편집")
        layout.addWidget(self.btn3)
        self.btn4 = QPushButton("시간표 삭제")
        layout.addWidget(self.btn4)