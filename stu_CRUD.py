from PyQt5.QtWidgets import *
from stu_connect import DB, config
import unicodedata


class Ins_lists(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowTitle("학생 추가")

        central = QWidget()
        self.setCentralWidget(central)
        v_box = QVBoxLayout(central)

        self.input_name = QLineEdit()
        self.input_hotspot = QLineEdit()

        v_box.addWidget(QLabel("학생 이름"))
        v_box.addWidget(self.input_name)
        v_box.addWidget(QLabel("핫스팟 이름"))
        v_box.addWidget(self.input_hotspot)
        self.btn_yes = QPushButton("확인")
        self.btn_yes.clicked.connect(self.ins_lists)
        v_box.addWidget(self.btn_yes)

    def ins_lists(self):
        name = self.input_name.text().strip()
        hotspot = self.input_hotspot.text().strip()
        if not name or not hotspot:
            QMessageBox.warning(self, "오류", "학생명과 핫스팟 이름을 모두 입력하세요.")
            return
        ok = self.db.insert_list(name, hotspot)
        if ok:
            QMessageBox.information(self, "완료", "추가되었습니다.")
            self.input_name.clear()
            self.input_hotspot.clear()
        else:
            QMessageBox.critical(self, "실패", "추가 중 오류가 발생하였습니다.")

class Upd_lists(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowTitle("학생 정보 수정")

        central = QWidget()
        self.setCentralWidget(central)
        v_box = QVBoxLayout(central)

        v_box.addWidget(QLabel("ID(필수 기입)"))
        self.code = QLineEdit()
        v_box.addWidget(self.code)
        v_box.addWidget(QLabel("학생 이름(공란 시 미반영)"))
        self.name = QLineEdit()
        v_box.addWidget(self.name)
        v_box.addWidget(QLabel("핫스팟 이름(공란 시 미반영)"))
        self.hotspot = QLineEdit()
        v_box.addWidget(self.hotspot)
        self.btn_yes = QPushButton("확인")
        self.btn_yes.clicked.connect(self.upd_lists)
        v_box.addWidget(self.btn_yes)

    def upd_lists(self):
        code = self.code.text().strip()
        if not code:
            QMessageBox.warning(self, "경고", "ID를 입력해 주십시오.")
            return

        result = self.db.find_list(code)
        
        if result == False:
            QMessageBox.warning(self, "오류", "검색된 데이터가 없습니다.")
            return
        else:
            name = self.name.text().strip()
            hotspot = self.hotspot.text().strip()

            ok = self.db.update_list(code, name, hotspot)

            if ok:
                QMessageBox.information(self, "완료", "수정되었습니다.")
                self.code.clear()
                self.name.clear()
                self.hotspot.clear()
            else:
                QMessageBox.critical(self, "실패", "수정 중 오류가 발생하였습니다.")

class Dlt_lists(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB(**config)

        self.setWindowTitle("학생 제거")

        central = QWidget()
        self.setCentralWidget(central)
        v_box = QVBoxLayout(central)

        self.input_id_or_hotspot = QLineEdit()

        v_box.addWidget(QLabel("ID 혹은 핫스팟 이름 입력"))
        v_box.addWidget(self.input_id_or_hotspot)
        self.btn_yes = QPushButton("확인")
        self.btn_yes.clicked.connect(self.dlt_lists)
        v_box.addWidget(self.btn_yes)

    def dlt_lists(self):
        id_or_hotspot = self.input_id_or_hotspot.text().strip()
        id_or_hotspot = unicodedata.normalize('NFKC', id_or_hotspot)

        if not id_or_hotspot:
            QMessageBox.warning(self, "오류", "ID 혹은 핫스팟 이름을 입력해주십시오.")
            return
        
        ok = self.db.verify_list(id_or_hotspot, id_or_hotspot)
        if ok:
            identify = self.db.delete_list(id_or_hotspot)
            if identify:
                QMessageBox.information(self, "완료", "제거되었습니다.")
                self.input_id_or_hotspot.clear()
            else:
                QMessageBox.critical(self, "실패", "오류가 발생하였습니다.")
        else:
            QMessageBox.critical(self, "실패", "존재하지 않는 데이터입니다.")