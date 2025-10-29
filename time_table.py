# 일일 시간표 관리 시스템
# 원하는 교시수를 선택 후 그 수에 맞는 표 db 생성
# 각 칸에 원하는 시간을 입력 및 db에 저장

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QPushButton, QTableWidget, QTimeEdit, QMessageBox
)
from PyQt5.QtCore import QTime, QDateTime
import mysql.connector
# from teacher_puls_1_2 import *

config = dict(
    host='localhost',
    user='root',
    password='000630',
    database='attenddb',
    charset='utf8'
)

class TimetableApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("일일 시간표 관리")
        self.resize(400, 500)

        self.layout = QVBoxLayout(self)

        # 교시 선택
        row_box = QHBoxLayout()
        row_box.addWidget(QLabel("교시 수:"))
        self.spin = QSpinBox()
        self.spin.setRange(1, 9)
        self.spin.setValue(5)
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

            # 종료시간은 spinbox 없이 읽기 전용 QTimeEdit
            end_edit = QTimeEdit()
            end_edit.setDisplayFormat("HH:mm")
            end_edit.setReadOnly(True)
            end_edit.setTime(QTime(9,50))
            self.table.setCellWidget(r, 1, end_edit)

    def update_end_time(self, row):
        start_widget = self.table.cellWidget(row, 0)
        end_widget = self.table.cellWidget(row, 1)
        start_time = start_widget.time()
        end_dt = QDateTime(QDateTime.currentDateTime().date(), start_time).addSecs(50*60) #50*60 3000초를 더함 이걸 수정해 간격 조정
        end_widget.setTime(end_dt.time())

    def save_to_db(self):
        try:
            conn = mysql.connector.connect(**config)
            cur = conn.cursor()

            # 테이블 생성
            cur.execute("""
                CREATE TABLE IF NOT EXISTS timetable (
                    period INT,
                    start_time TIME,
                    end_time TIME
                )
            """)

            # 기존 데이터 삭제
            cur.execute("DELETE FROM timetable")

            # 데이터 삽입
            for r in range(self.table.rowCount()):
                start_widget = self.table.cellWidget(r, 0)
                end_widget = self.table.cellWidget(r, 1)
                start_str = start_widget.time().toString("HH:mm")
                end_str = end_widget.time().toString("HH:mm")
                cur.execute(
                    "INSERT INTO timetable (period, start_time, end_time) VALUES (%s, %s, %s)",
                    (r+1, start_str, end_str)
                )

            conn.commit()
            QMessageBox.information(self, "저장 완료", "MySQL DB에 저장되었습니다.")
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "DB 오류", f"MySQL 작업 중 오류 발생:\n{e}")
        finally:
            try:
                if conn:
                    conn.close()
            except NameError:
                pass
