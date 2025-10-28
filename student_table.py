import sys
import pymysql
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel,
    QLineEdit, QPushButton, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt

# MySQL 접속 정보
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123",
    "database": "sampledb",
    "charset": "utf8"
}

class StudentsTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학생 관리")
        self.resize(1200, 500)

        layout = QVBoxLayout()

        # 입력 칸 (이름 추가용)
        form_layout = QHBoxLayout()
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("이름 (추가용)")

        self.btn_add = QPushButton("추가")
        self.btn_add.clicked.connect(self.add_student)

        # 출석 체크 버튼
        self.btn_attendance = QPushButton("1교시 출석 체크")
        self.btn_attendance.clicked.connect(self.attendance_1col)

        form_layout.addWidget(QLabel("이름:"))
        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.btn_add)
        form_layout.addWidget(self.btn_attendance)
        layout.addLayout(form_layout)

        # 테이블
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # 내부 저장용
        self.student_ids = []
        self.load_data()

    def load_data(self):
        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students ORDER BY id")
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

            self.student_ids = [row[0] for row in rows]

            display_columns = columns[1:] + ["삭제"]  # id 제외 + 삭제 버튼
            self.table.setColumnCount(len(display_columns))
            self.table.setRowCount(len(rows))
            self.table.setHorizontalHeaderLabels(display_columns)

            for r, row in enumerate(rows):
                for c, value in enumerate(row[1:]):  # id 제외
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(r, c, item)

                # 삭제 버튼
                btn = QPushButton("삭제")
                btn.clicked.connect(lambda checked, idx=r: self.del_student_by_row(idx))
                self.table.setCellWidget(r, len(display_columns)-1, btn)

            self.table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"DB 조회 실패: {e}")
        finally:
            conn.close()

    def add_student(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "오류", "이름을 입력하세요.")
            return

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                # total 컬럼은 GENERATED라 제외, 1~8은 기본값 0
                cur.execute("INSERT INTO students (name) VALUES (%s)", (name,))
            conn.commit()
            self.input_name.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"추가 실패: {e}")
        finally:
            conn.close()

    def del_student_by_row(self, row_index):
        student_id = self.student_ids[row_index]
        reply = QMessageBox.question(self, "삭제 확인", "학생을 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("DELETE FROM students WHERE id=%s", (student_id,))
            conn.commit()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"삭제 실패: {e}")
        finally:
            conn.close()

    def attendance_1col(self):
        # 출석 체크 대상 이름 리스트
        attendance_list = ["홍길동", "유재석"]  # 출석한 학생 이름
        print("출석 체크 대상:", attendance_list)

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                for name in attendance_list:
                    cur.execute("UPDATE students SET `1`=1 WHERE name=%s", (name,))
            conn.commit()
            QMessageBox.information(self, "완료", "1교시 출석 체크 완료!")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"출석 체크 실패: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StudentsTable()
    win.show()
    sys.exit(app.exec_())
