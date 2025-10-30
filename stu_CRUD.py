from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from stu_connect import DB, config
from month_table import sync_add_student, sync_update_student
import traceback
import unicodedata


class Ins_lists(QMainWindow):
    data_changed_i = pyqtSignal()  # ✅ 부모창에 보낼 신호

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

        try:
            ok = self.db.insert_list(name, hotspot)

            if ok:
                # monthtb에도 추가 (예외 방지용 try)
                try:
                    sync_add_student(name, hotspot)
                except Exception as e:
                    print("⚠️ monthtb 동기화 실패:", e)
                    traceback.print_exc()

                QMessageBox.information(self, "완료", "학생이 추가되었습니다.")
                self.data_changed_i.emit()  # ✅ 부모창에 신호
                self.close()                # ✅ 창 닫기
            else:
                QMessageBox.critical(self, "실패", "DB에 학생을 추가하는 중 오류가 발생했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"학생 추가 중 오류 발생:\n{e}")
            traceback.print_exc()

class Upd_lists(QMainWindow):
    data_changed_u = pyqtSignal()  # ✅ 부모창에 보낼 신호

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

    def update_list(self, id, name=None, hotspot=None):
        sql_first = "UPDATE dailytb SET "
        sql_last = " WHERE id=%s"

        set_clauses = []
        values = []

        if name:
            set_clauses.append("name=%s")
            values.append(name)

        if hotspot:
            set_clauses.append("hotspot=%s")
            values.append(hotspot)

        if not set_clauses:
            return False

        sql = sql_first + ", ".join(set_clauses) + sql_last
        values.append(id)

        with self.connect() as con:
            try:
                with con.cursor() as cur:
                    # 기존 hotspot 가져오기
                    cur.execute("SELECT hotspot FROM dailytb WHERE id=%s", (id,))
                    old_hotspot = cur.fetchone()
                    if old_hotspot:
                        old_hotspot = old_hotspot[0]
                    else:
                        return False  # id 존재하지 않음

                    cur.execute(sql, values)
                    affected = cur.rowcount

                    if affected > 0:
                        # monthtb 동기화
                        sync_update_student(
                            old_hotspot,
                            name if name else "", 
                            hotspot if hotspot else old_hotspot
                        )
                    else:
                        con.rollback()
                        return False

                    con.commit()
                    return True
            except Exception as e:
                print("오류 코드>", e)
                con.rollback()
                return False
            
class Dlt_lists(QMainWindow):
    data_changed_d = pyqtSignal()  # ✅ 부모창에 보낼 신호

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
        
        try:
            ok = self.db.verify_list(id_or_hotspot, id_or_hotspot)
            if ok:
                identify = self.db.delete_list(id_or_hotspot)
                if identify:
                    QMessageBox.information(self, "완료", "제거되었습니다.")
                    self.data_changed_d.emit()  # ✅ 부모창에 즉시 신호
                    self.close()              # ✅ 창 닫기
                    self.input_id_or_hotspot.clear()
                else:
                    QMessageBox.critical(self, "실패", "오류가 발생하였습니다.")
            else:
                QMessageBox.critical(self, "실패", "존재하지 않는 데이터입니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"학생 추가 중 오류 발생:\n{e}")
            traceback.print_exc()