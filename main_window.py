from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QPushButton, QMessageBox
from db_helper import DB, DB_CONFIG
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원 관리")
        self.db = DB(**DB_CONFIG)

        #중앙 위젯 및 레이아웃
        central = QWidget()
        self.setCentralWidget(central)
        vbox =QVBoxLayout(central)

        #상단: 입력폼 +추가 버튼
        form_box = QHBoxLayout()
        self.input_name = QLineEdit()
        self.input_email = QLineEdit()
        self.btn_add = QPushButton("추가")
        self.btn_add.clicked.connect(self.add_member)


        #상단: 입력폼 +제거 버튼
        self.btn_del = QPushButton("제거")
        self.btn_del.clicked.connect(self.del_member)


        form_box.addWidget(QLabel("이름"))
        form_box.addWidget(self.input_name)
        form_box.addWidget(QLabel("이메일"))
        form_box.addWidget(self.input_email)
        form_box.addWidget(self.btn_add)
        form_box.addWidget(self.btn_del)

        #중앙: 테이블 위젯
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID","이름","이메일"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        #배치

        vbox.addLayout(form_box)
        vbox.addWidget(self.table)

        #초기 데이터 로드
        self.load_members()

    def load_members(self):
        rows = self.db.fetch_members()
        self.table.setRowCount(len(rows))
        for r,(mid,name,email) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(mid)))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(email))
        self.table.resizeColumnsToContents()

    def add_member(self):
        name = self.input_name.text().strip()
        email = self.input_email.text().strip()
        if not name or not email:
            QMessageBox.warning(self,"오류", "이름과 이메일을 모두 입력하세요.")
            return
        ok = self.db.insert_member(name,email)
        if ok:
            QMessageBox.information(self,"완료","추가했습니다")
            self.input_name.clear()
            self.input_email.clear()
            self.load_members()
        else:
            QMessageBox.critical(self,"실패","추가 중 오류가 발생했습니다.")

    def del_member(self):
        name = self.input_name.text().strip()
        email = self.input_email.text().strip()
        if not name or not email:
            QMessageBox.warning(self, "오류", "이름과 이메일을 모두 입력하세요.")
            return
        ok = self.db.delete_member(name, email)  # 삭제를 위한 DB 호출
        if ok:
            QMessageBox.information(self, "완료", "삭제했습니다")
            self.input_name.clear()
            self.input_email.clear()
            self.load_members()
        else:
            QMessageBox.critical(self, "실패", "삭제 중 오류가 발생했습니다.")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
