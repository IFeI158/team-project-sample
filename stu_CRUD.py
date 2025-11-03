from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from stu_connect import DB, config
from month_table import sync_add_student, sync_update_student, sync_delete_student
import traceback
import unicodedata
from PyQt5.QtGui import *


class Ins_lists(QMainWindow):
    data_changed_i = pyqtSignal()  # ✅ 부모창에 보낼 신호

    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowTitle("학생 추가")
        self.setWindowIcon(QIcon("stu.png"))

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
        self.setWindowIcon(QIcon("stu.png"))

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
        id = self.code.text().strip()
        name = self.name.text().strip()
        hotspot = self.hotspot.text().strip()

        if not id:
            QMessageBox.warning(self, "오류", "ID를 입력해야 합니다.")
            return

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
            QMessageBox.warning(self, "오류", "변경할 값을 입력하세요.")
            return

        sql = sql_first + ", ".join(set_clauses) + sql_last
        values.append(id)

        con = self.db.connect()  # ✅ 수정된 부분
        try:
            with con.cursor() as cur:
                cur.execute("SELECT hotspot FROM dailytb WHERE id=%s", (id,))
                old_hotspot = cur.fetchone()
                if not old_hotspot:
                    QMessageBox.warning(self, "오류", "해당 ID가 존재하지 않습니다.")
                    return
                old_hotspot = old_hotspot[0]

                cur.execute(sql, values)
                affected = cur.rowcount

                if affected > 0:
                    sync_update_student(old_hotspot, name, hotspot)
                    con.commit()
                    QMessageBox.information(self, "완료", "수정이 완료되었습니다.")
                    self.data_changed_u.emit()
                    self.close()
                else:
                    con.rollback()
                    QMessageBox.warning(self, "실패", "수정된 데이터가 없습니다.")
        except Exception as e:
            con.rollback()
            QMessageBox.critical(self, "오류", f"수정 중 오류 발생:\n{e}")
            traceback.print_exc()
        finally:
            con.close()

            
class Dlt_lists(QMainWindow):
    data_changed_d = pyqtSignal()  # ✅ 부모창에 보낼 신호

    def __init__(self):
        super().__init__()
        self.db = DB(**config)
        self.setWindowIcon(QIcon("stu.png"))

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
                identify = self.delete_list(id_or_hotspot)
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

    def delete_list(self, id_or_hotspot):
        sql_id = "DELETE FROM dailytb WHERE id=%s"
        sql_id_to_hotspot = "SELECT hotspot FROM dailytb WHERE id=%s"
        sql_hotspot = "DELETE FROM dailytb WHERE hotspot=%s"

        db = DB(**config)  # ✅ DB 객체 생성
        con = db.connect()  # ✅ 커넥션 획득

        try:
            with con.cursor() as cur:
                if id_or_hotspot.isdigit():
                    cur.execute(sql_id_to_hotspot, (int(id_or_hotspot),))
                    hotspot_from_id = cur.fetchone()
                    if hotspot_from_id:
                        hotspot_from_id = hotspot_from_id[0]
                        sync_delete_student(hotspot_from_id)
                    cur.execute(sql_id, (int(id_or_hotspot),))
                else:
                    cur.execute(sql_hotspot, (id_or_hotspot,))
                    sync_delete_student(id_or_hotspot)
                con.commit()
                return True
        except Exception as e:
            con.rollback()
            print("삭제 오류:", e)
            return False
        finally:
            con.close()  # ✅ 연결 닫기