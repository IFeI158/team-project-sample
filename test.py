import sys
from PyQt5.QtWidgets import *
from stu_main import *
from month_table import *
from time_table import TimetableApp
import subprocess
import os

config = dict(
    host='localhost',
    user='root',
    password='123',
    database='attenddb',
    charset='utf8'
)

class TimeTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("시간표")
        self.setGeometry(200, 200, 600, 400)

        # 위젯 세팅
        self.table = QTableWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # DB 데이터 불러오기
        self.load_timetable()

    def load_timetable(self):
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        query = "SELECT * FROM timetable"  # 테이블 전체 출력
        cursor.execute(query)
        data = cursor.fetchall()

        # 컬럼명 읽기
        columns = [desc[0] for desc in cursor.description]

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # 데이터 테이블에 넣기
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        cursor.close()
        conn.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = TimeTableWindow()
    win.show()
    sys.exit(app.exec_())
