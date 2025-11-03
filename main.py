import sys
from PyQt5.QtWidgets import *
from stu_main import *
from month_table import *
from time_table import TimetableApp
from PyQt5.QtGui import *
import subprocess
import os

def run_linked_well_task():
    script_path = os.path.join(os.getcwd(), "linked_well.py")
    try:
        subprocess.Popen([sys.executable, script_path])  # ✅ run → Popen으로 변경
        print(f"[실행 중] {script_path}")
    except Exception as e:
        print(f"❌ linked_well.py 실행 오류: {e}")

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 340, 400)
        self.setWindowTitle("관리자 모드")
        self.setWindowIcon(QIcon("tik.png"))
        self.timetable_window = None
        
        #  메인 위젯 & 레이아웃
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        #  버튼
        self.btn1 = QPushButton("시간표 관리")
        self.btn1.clicked.connect(self.open_timetable)
        self.btn1.setStyleSheet("""
            QPushButton {
                border: 2px solid black; 
                border-radius: 11px;
                color: black;
                font-weight: bold;
                font-size: 16pt;
                background-color: #FFC0CB;  /* 분홍 */
            }
            QPushButton:hover {
                background-color: #FFD6E0;  /* 연분홍 */
            }
            QPushButton:pressed {
                background-color: #FF69B4;  /* 진분홍 */
            }
        """)
        layout.addWidget(self.btn1)

        self.btn2 = QPushButton("학생 관리")
        self.btn2.clicked.connect(self.stumain)
        self.btn2.setStyleSheet("""
            QPushButton {
                border: 2px solid black; 
                border-radius: 11px;
                color: black;
                font-weight: bold;
                font-size: 16pt;
                background-color: #FFFF99;  /* 노랑 */
            }
            QPushButton:hover {
                background-color: #FFFFCC;  /* 조금 더 연한 노랑 */
            }
            QPushButton:pressed {
                background-color: #FFD700;  /* 진한 노랑 */
            }
        """)
        layout.addWidget(self.btn2)

        self.btn3 = QPushButton("출결 관리")
        self.btn3.clicked.connect(self.montable)
        self.btn3.setStyleSheet("""
            QPushButton {
                border: 2px solid black; 
                border-radius: 11px;
                color: black;
                font-weight: bold;
                font-size: 16pt;
                background-color: #87CEFA;  /* 하늘 */
            }
             QPushButton:hover {
                background-color: #B0E0FF;  /* 연하늘 */
            }
            QPushButton:pressed {
                background-color: #4682B4;  /* 진한 하늘 */
            }
        """)
        layout.addWidget(self.btn3)

        # 테이블 위젯
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # 데이터 로드
        self.load_timetable()

    def stumain(self):
        self.ins = SWindow()
        self.ins.show()

    def montable(self):
        self.ins = AttendanceTable()
        self.ins.show()
    
    def open_timetable(self):
        if self.timetable_window is None:
            self.timetable_window = TimetableApp()
            self.timetable_window.updated.connect(self.load_timetable)
        self.timetable_window.show()
        self.timetable_window.raise_()
        self.timetable_window.activateWindow()
    
    def load_timetable(self):
        db = DB(**config)
        conn = db.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM timetable"  # 테이블 전체 출력
        cursor.execute(query)
        data = cursor.fetchall()

        # 컬럼명 읽기
        columns = [desc[0] for desc in cursor.description]

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 데이터 테이블에 넣기
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()



    

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
    run_linked_well_task()
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_() # 별도 동작이 없을 경우, 실행 중인 명령(.show())을 유지.