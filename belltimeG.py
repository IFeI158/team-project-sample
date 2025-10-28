import sys
import serial
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer

# Arduino 포트 설정
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Arduino 초기화 대기

class AlarmApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino 알람")
        self.setGeometry(200, 200, 300, 150)
        self.target_hour = None
        self.target_minute = None

        # UI 구성
        layout = QVBoxLayout()

        self.label = QLabel("알람 시간 입력 (HH:MM):")
        layout.addWidget(self.label)

        self.time_input = QLineEdit()
        layout.addWidget(self.time_input)

        self.btn_set = QPushButton("알람 설정")
        self.btn_set.clicked.connect(self.set_alarm)
        layout.addWidget(self.btn_set)

        self.setLayout(layout)

        # 타이머 설정 (1초마다 체크)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time)
        self.timer.start(1000)

    def set_alarm(self):
        time_text = self.time_input.text()
        try:
            parts = time_text.split(":")
            self.target_hour = int(parts[0])
            self.target_minute = int(parts[1])
            QMessageBox.information(self, "설정 완료", f"알람이 {self.target_hour:02d}:{self.target_minute:02d}로 설정되었습니다.")
        except:
            QMessageBox.warning(self, "오류", "시간 형식이 잘못되었습니다. HH:MM 형태로 입력하세요.")

    def check_time(self):
        if self.target_hour is None or self.target_minute is None:
            return

        now = datetime.now()
        if now.hour == self.target_hour and now.minute == self.target_minute:
            arduino.write(b'P')  # Arduino에 신호 전송
            QMessageBox.information(self, "알람", "설정한 시간입니다! 멜로디 재생")
            # 한 번 실행 후 타이머 중지
            self.timer.stop()

app = QApplication(sys.argv)
window = AlarmApp()
window.show()
sys.exit(app.exec_())
