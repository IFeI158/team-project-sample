import sys
from PyQt5.QtWidgets import *
from stu_connect import DB, config
from stu_CRUD import Ins_lists, Upd_lists, Dlt_lists


class SWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학생 관리")
        self.db = DB(**config)

        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        form_box = QHBoxLayout()
        self.searchbar = QLineEdit()
        form_box.addWidget(QLabel("핫스팟 검색"))
        self.searchbar.returnPressed.connect(self.search)
        form_box.addWidget(self.searchbar)

        self.btn_ld = QPushButton("새로고침")
        self.btn_ld.clicked.connect(self.load_lists)
        form_box.addWidget(self.btn_ld)

        # self.btn_upd = QPushButton("학생 수정")
        # self.btn_upd.clicked.connect(self.upd_btn)
        # form_box.addWidget(self.btn_upd)

        small_vbox = QVBoxLayout()
        self.btn_add = QPushButton("학생 추가")
        self.btn_add.clicked.connect(self.ins_btn)
        self.btn_dlt = QPushButton("학생 제거")
        self.btn_dlt.clicked.connect(self.dlt_btn)
        small_vbox.addWidget(self.btn_add)
        small_vbox.addWidget(self.btn_dlt)
        form_box.addLayout(small_vbox)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "학생 이름", "핫스팟 이름", "출결 점수"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        vbox.addLayout(form_box)
        vbox.addWidget(self.table)

        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.load_lists()

    def load_lists(self):
        rows = self.db.fetch_list_id()
        self.table.setRowCount(len(rows))
        for r, (id, name, hotspot, daily_score) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(id)))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(str(hotspot)))
            self.table.setItem(r, 3, QTableWidgetItem(str(daily_score)))

    def search(self):
        inputval = self.searchbar.text().strip()
        if not inputval:  # None 대신 공백 체크
            return
        try:
            result = self.db.find_list(inputval)  # fetchall → 리스트[튜플]
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "오류", "뭔가 잘못되었습니다.")
            return

        if result:
            self.table.setRowCount(len(result))         # 행 개수
            self.table.setColumnCount(len(result[0]))   # 열 개수

            for row, row_data in enumerate(result):     # 각 행 순회
                for col, value in enumerate(row_data):  # 각 열 순회
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        else:
            QMessageBox.warning(self, "오류", "검색된 데이터가 없습니다.")

    def ins_btn(self):
        self.ins = Ins_lists()
        self.ins.show()

    def upd_btn(self):
        self.upd = Upd_lists()
        self.upd.show()
    
    def dlt_btn(self):
        self.dlt = Dlt_lists()
        self.dlt.show()

#if __name__ == "stu_main":
#    app = QApplication(sys.argv)
#    myWindow = SWindow()
#    myWindow.show()
#    app.exec_()