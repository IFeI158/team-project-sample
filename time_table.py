# time_table.py - 안정화 버전
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QPushButton, QTableWidget, QTimeEdit, QMessageBox
)
from PyQt5.QtCore import QTime, QDateTime, pyqtSignal
import pymysql
from PyQt5.QtGui import *
from stu_connect import DB, config

# DB 접속 정보
db = DB(**config)
conn = db.connect()
cursor = conn.cursor()

class TimetableApp(QWidget):
    updated = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("일일 시간표 관리")
        self.resize(400, 500)
        self.setWindowIcon(QIcon("tik.png"))

        self.layout = QVBoxLayout(self)

        # 교시 선택
        row_box = QHBoxLayout()
        row_box.addWidget(QLabel("교시 수:"))
        self.spin = QSpinBox()
        self.spin.setRange(1, 9)
        row_box.addWidget(self.spin)

        self.btn_apply = QPushButton("표 생성")
        self.btn_apply.clicked.connect(self.create_table)
        row_box.addWidget(self.btn_apply)

        self.layout.addLayout(row_box)

        # 테이블
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # 저장 버튼
        self.btn_save = QPushButton("저장")
        self.btn_save.clicked.connect(self.save_to_db)
        self.layout.addWidget(self.btn_save)

        self.create_table()

    def create_table(self):
        rows = self.spin.value()
        self.table.setRowCount(rows)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["시작 시간", "종료 시간"])
        self.table.setVerticalHeaderLabels([f"{i+1}교시" for i in range(rows)])

        for r in range(rows):
            start_edit = QTimeEdit()
            start_edit.setDisplayFormat("HH:mm")
            start_edit.setTime(QTime(9,0))
            start_edit.timeChanged.connect(lambda time, row=r: self.update_end_time(row))
            self.table.setCellWidget(r, 0, start_edit)

            end_edit = QTimeEdit()
            end_edit.setDisplayFormat("HH:mm")
            end_edit.setReadOnly(True)
            end_edit.setTime(QTime(9,50))
            self.table.setCellWidget(r, 1, end_edit)

    def update_end_time(self, row):
        start_widget = self.table.cellWidget(row, 0)
        end_widget = self.table.cellWidget(row, 1)
        start_time = start_widget.time()
        # 50분 후로 종료시간 설정
        end_dt = QDateTime(QDateTime.currentDateTime().date(), start_time).addSecs(50*60)
        end_widget.setTime(end_dt.time())

    def save_to_db(self):
        conn = None
        try:
            # DB 연결
            conn = pymysql.connect(**config)
            cur = conn.cursor()

            # 테이블 생성
            cur.execute("""
                CREATE TABLE IF NOT EXISTS timetable (
                    period INT PRIMARY KEY,
                    start_time TIME,
                    end_time TIME
                )
            """)
            conn.commit()

            # 기존 데이터 삭제
            cur.execute("DELETE FROM timetable")

            # 시간표 데이터 수집
            times = []
            for r in range(self.table.rowCount()):
                start_widget = self.table.cellWidget(r, 0)
                end_widget = self.table.cellWidget(r, 1)
                start_time = start_widget.time()
                end_time = end_widget.time()

                # 시작과 종료 시간이 같으면 오류
                if start_time == end_time:
                    QMessageBox.warning(self, "시간 오류", f"{r+1}교시의 시작과 종료 시간이 같습니다.")
                    return

                times.append((r+1, start_time, end_time))

            # 모든 교시 쌍 비교
            for i in range(len(times)):
                period_i, start_i, end_i = times[i]
                for j in range(i+1, len(times)):
                    period_j, start_j, end_j = times[j]

                    # 교시 순서를 보장하기 위해 start_i <= start_j로 정렬 후 비교
                    if start_i > start_j:
                        start_i, end_i, start_j, end_j = start_j, end_j, start_i, end_i

                    if start_j < end_i:
                        QMessageBox.warning(self, "시간 겹침 오류",
                                            f"{period_i}교시와 {period_j}교시의 시간이 겹칩니다.")
                        return

            # DB에 저장
            for period, start, end in times:
                cur.execute(
                    "INSERT INTO timetable (period, start_time, end_time) VALUES (%s, %s, %s)",
                    (period, start.toString("HH:mm:ss"), end.toString("HH:mm:ss"))
                )
            conn.commit()
            QMessageBox.information(self, "저장 완료", "DB에 저장되었습니다.")
            self.updated.emit()

        except Exception as e:
            QMessageBox.critical(self, "DB 오류", f"저장 중 오류 발생:\n{e}")

        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass



