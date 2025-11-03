import calendar
from datetime import datetime
from PyQt5.QtWidgets import QPushButton, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtGui import *
from stu_connect import DB, config

db = DB(**config)
conn = db.connect()
cursor = conn.cursor()

# --------------------------
# 이번달 설정
# --------------------------
now = datetime.now()
year = now.year
month = now.month
_, last_day = calendar.monthrange(year, month)


# --------------------------
# 학생 CRUD 연동 함수
# --------------------------

def sync_add_student(name, hotspot):
    # 새 학생 추가 시 monthtb에도 반영
    for day in range(1, last_day + 1):
        weekday = datetime(year, month, day).weekday()
        if weekday < 5:
            cursor.execute("""
                INSERT IGNORE INTO monthtb (day, hotspot_name, name, daily_total, month_total)
                VALUES (%s, %s, %s, 0, 0)
            """, (day, hotspot, name))
    conn.commit()


def sync_delete_student(hotspot):
    # 학생 삭제 시 monthtb에서도 제거
    cursor.execute("DELETE FROM monthtb WHERE hotspot_name = %s", (hotspot,))
    conn.commit()


def sync_update_student(old_hotspot, new_name=None, new_hotspot=None):
    # 기존 데이터 가져오기
    cursor.execute("SELECT name, hotspot_name FROM monthtb WHERE hotspot_name=%s", (old_hotspot,))
    row = cursor.fetchone()
    if not row:
        return
    current_name, current_hotspot = row

    # 공란이면 기존 값 유지
    final_name = new_name if new_name else current_name
    final_hotspot = new_hotspot if new_hotspot else current_hotspot

    cursor.execute("""
        UPDATE monthtb
        SET name=%s, hotspot_name=%s
        WHERE hotspot_name=%s
    """, (final_name, final_hotspot, old_hotspot))
    conn.commit()


# --------------------------
# 하루 종료 시: dailytb → monthtb 반영
# --------------------------
def move_daily_to_month(today_day):
    cursor.execute("SELECT name, hotspot, daily_score FROM dailytb")
    for name, hotspot_name, daily_score in cursor.fetchall():
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


# --------------------------
# PyQt5 GUI
# --------------------------
class AttendanceTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Attendance Table - {now.year}년 {now.month}월")
        self.resize(1200, 600)
        self.setWindowIcon(QIcon("cal.png"))

        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.btn_init = QPushButton("보드 초기화 및 최종 정산")
        self.btn_init.clicked.connect(self.init_monthtb)
        layout.addWidget(self.btn_init)

        self.load_data()

    def load_data(self):
        # 이번 달 평일 리스트
        days = [day for day in range(1, last_day+1) if datetime(year, month, day).weekday() < 5]
        columns = ["name", "hotspot_name"] + [str(d) for d in days] + ["total"]
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
    # monthtb 초기화 (새 달)
    # --------------------------
    def init_monthtb(self):
        # 월 전체 초기화 + historyDB 백업

        # --------------------------
        # historyDB 연결
        # --------------------------
        cursor.execute("""
            CREATE DATABASE IF NOT EXISTS historyDB
            DEFAULT CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
        """)
        cursor.execute("USE historyDB;")

        hist_table_name = f"{year}_{month:02d}"  # ex) 2025_10
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {hist_table_name} (
                name VARCHAR(50),
                hotspot_name VARCHAR(50),
                month_total INT,
                status VARCHAR(10),
                PRIMARY KEY (hotspot_name)
            );
        """)

        # --------------------------
        # attenddb에서 monthtb 가져와 백업
        # --------------------------
        cursor.execute("USE attenddb;")
        cursor.execute("SELECT name, hotspot_name, month_total FROM monthtb")

        # ✅ 이번 달 실제 평일 수 계산
        weekday_count = sum(
            1 for day in range(1, last_day + 1)
            if datetime(year, month, day).weekday() < 5
        )

        # ✅ 평일 수 기준 통과 커트라인
        passing_score = weekday_count * 3 * 4 / 5

        # ✅ historyDB에 데이터 백업 + 통과/탈락 계산
        for name, hotspot_name, month_total in cursor.fetchall():
            status = "통과" if month_total >= passing_score else "탈락"

            cursor.execute(f"""
                REPLACE INTO historyDB.{hist_table_name}
                (name, hotspot_name, month_total, status)
                VALUES (%s, %s, %s, %s)
            """, (name, hotspot_name, month_total, status))

        conn.commit()

        # --------------------------
        # monthtb 초기화 (새 달 준비)
        # --------------------------
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

        QMessageBox.information(self, "완료", f"이번 달({month}월) 데이터 초기화 및 백업 완료.")
        self.load_data()
