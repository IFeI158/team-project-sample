import calendar
from datetime import datetime
import pymysql
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout

# --------------------------
# MySQL 연결
# --------------------------
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123',
    database='attenddb',
    charset='utf8mb4'
)
cursor = conn.cursor()

# --------------------------
# 이번달 설정
# --------------------------
now = datetime.now()
year = now.year
month = now.month
_, last_day = calendar.monthrange(year, month)

# --------------------------
# monthtb 생성 (평일만, daily_score = 0)
# --------------------------
def init_monthtb():
    # 기존 데이터 삭제 및 이번달 평일만 추려내어 새 표 생성(새로운 달 생성 시 이용)
    cursor.execute("DELETE FROM monthtb;")

    for day in range(1, last_day + 1):
        weekday = datetime(year, month, day).weekday()
        if weekday < 5:  # 평일만
            cursor.execute("SELECT name, hotspot FROM dailytb")
            for name, hotspot_name in cursor.fetchall():
                cursor.execute("""
                    INSERT INTO monthtb (day, hotspot_name, name, daily_total, month_total)
                    VALUES (%s, %s, %s, 0, 0)
                """, (day, hotspot_name, name))
    conn.commit()

# --------------------------
# 하루 종료 시: dailytb -> monthtb 전송
# --------------------------
def move_daily_to_month(today_day):
    cursor.execute("SELECT name, hotspot, daily_score FROM dailytb")
    for name, hotspot_name, daily_score in cursor.fetchall():
        # 점수 변환 로직
        if 0 <= daily_score <= 3:
            converted_score = 0
        elif 4 <= daily_score < 7:
            converted_score = 2
        else:
            converted_score = 3

    # 월간 테이블 업데이트
    cursor.execute("""
        UPDATE monthtb
        SET daily_total = %s,
        month_total = month_total + %s
        WHERE day = %s AND name = %s AND hotspot_name = %s
    """, (converted_score, converted_score, today_day, name, hotspot_name))
    cursor.execute("UPDATE dailytb SET daily_score = 0")
    conn.commit()

# 일일 점수 초기화
def init_daily_score(endclass):

    endclass

    cursor.execute("UPDATE dailytb SET daily_score = 0")

# --------------------------
# PyQt5 GUI
# --------------------------
class AttendanceTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Attendance Table - {now.year}년 {now.month}월")
        self.resize(1200, 600)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        # 이번 달 평일 리스트
        days = [day for day in range(1, last_day+1) if datetime(year, month, day).weekday() < 5]
        columns = ["name", "hotspot_name"] + [str(d) for d in days] + ["total"]
#        columns = ["name", "hotspot"] + [str(d) for d in days] + ["total"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # 모든 사용자
        cursor.execute("SELECT DISTINCT name, hotspot_name FROM monthtb")
        users = cursor.fetchall()

        self.table.setRowCount(len(users))
        for row_idx, (name, hotspot_name) in enumerate(users):
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(hotspot_name))

            total = 0
            for col_idx, day in enumerate(days, start=2):
                cursor.execute("""
                    SELECT daily_total FROM monthtb
                    WHERE name=%s AND hotspot_name=%s AND day=%s
                """, (name, hotspot_name, day))
                result = cursor.fetchone()
                score = result[0] if result else 0
                total += score
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(score)))

            self.table.setItem(row_idx, len(columns)-1, QTableWidgetItem(str(total)))

# --------------------------
# 실행
# --------------------------
# if __name__ == "month_table":
#    init_monthtb()           # 월 초기화
#    move_daily_to_month(now.day)   # 예시: 오늘(10월 28일) 점수 전송

#    app = QApplication(sys.argv)
#    window = AttendanceTable()
#    window.show()
#    sys.exit(app.exec_())