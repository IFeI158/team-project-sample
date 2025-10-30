import sys
from PyQt5.QtWidgets import *
from stu_main import *
from month_table import *
from time_table import TimetableApp

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowTitle("관리자 모드")
        self.timetable_window = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.btn1 = QPushButton("시간표 관리")
        self.btn1.clicked.connect(self.open_timetable)
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
        # init_monthtb()           # 월 초기화
        # move_daily_to_month(1)   # 예시: 오늘(10월 29일) 점수 전송
        self.ins = AttendanceTable()
        self.ins.show()
    
    def open_timetable(self):
        if self.timetable_window is None:
            self.timetable_window = TimetableApp()
        self.timetable_window.show()
        self.timetable_window.raise_()
        self.timetable_window.activateWindow()
    

# 메인 기능
# 시간표 관리 : 시간표 조회, 추가/편집/삭제 QSpinbox "DEVICE CONTROL"
# 학생 관리 : 학생 목록 조회, 추가/편집/삭제, 출석현황 수정, 정산 "DEVICE CONTROL"

# month_table.py 에서 day_to_month 라는 func. 거기서 daily_score 를 -> daily_total로 넘기면서, 초기화 0으로

# 오늘 날짜를 가져와서 대조 -> 오늘이 아님(지남) -> 자동으로 daily_score 0으로 초기화 => 테이블에 오늘 날짜가 있음

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