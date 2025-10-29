import sys
from PyQt5.QtWidgets import *
from dbconnect import DB, config
from stu_main import *
from month_table import *

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowTitle("관리자 모드")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.btn1 = QPushButton("시간표 관리")
        layout.addWidget(self.btn1)
        self.btn2 = QPushButton("학생 관리")
        self.btn2.clicked.connect(self.stumain)
        layout.addWidget(self.btn2)
        self.btn3 = QPushButton("출결 관리")
        self.btn3.clicked.connect(self.montable)
        layout.addWidget(self.btn3)

    def stumain(self):
        self.ins = SWindow()
        self.ins.show()

    def montable(self):
        ins_monthtb()           # 월 초기화
        move_daily_to_month(now.day)   # 예시: 오늘(10월 29일) 점수 전송
        self.ins = AttendanceTable()
        self.ins.show()

    

# 메인 기능
# 시간표 관리 : 시간표 조회, 추가/편집/삭제 QSpinbox "DEVICE CONTROL"
# 학생 관리 : 학생 목록 조회, 추가/편집/삭제, 출석현황 수정, 정산 "DEVICE CONTROL"
# 출결 관리 : 날짜별 출석 점수 조회, 편집 "+@"
# 모듈화 : serial 연동 모듈, db 연동 모듈, 메인윈도우, 금일 출석체크, 출석 저널(월간), 저널(history)

# 서브 기능
# 아두이노 부저 : 벨소리 추가, 편집 (SQL 연동) "DEVICE CONTROL"

# 부가 기능
# 관리자 로그인 시스템 : injection 방지 "+@"


if __name__ == "__main__":  # 실행 환경이 해당 파일(모듈로 import되지 않은 '__main__')이면 실행
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_() # 별도 동작이 없을 경우, 실행 중인 명령(.show())을 유지.