import pymysql
from month_table import sync_delete_student

config = dict(
    host = 'localhost',
    user = 'root',
    password = '123',
    database = 'attenddb',
    charset = 'utf8'
)

class DB:
    def __init__(self, **CONFIG):
        self.config = CONFIG

    def connect(self):
        return pymysql.connect(**self.config)

    # 값 추적
    def verify_list(self, id, hotspot):
        sql = "SELECT COUNT(*) FROM dailytb WHERE id=%s or hotspot=%s"
        with self.connect() as con:
            with con.cursor() as cur:
                cur.execute(sql, (id, hotspot))
                count, = cur.fetchone() # 자료형이 튜플임.
                return count == 1

    def find_list(self, id_or_hotspot):
        sql_id = "SELECT * FROM dailytb WHERE id=%s"
        sql_name = "SELECT * FROM dailytb WHERE hotspot=%s"
        with self.connect() as con:
            with con.cursor() as cur:
                try:
                    if id_or_hotspot.isdigit():
                        cur.execute(sql_id, int(id_or_hotspot))
                    else:
                        cur.execute(sql_name, id_or_hotspot)
                    return cur.fetchall()
                except Exception:
                    return False

    # 정렬 ( ID순 )
    def fetch_list_id(self):
        sql = "SELECT * FROM dailytb ORDER BY id"
        with self.connect() as con:
            with con.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # 값 추가            
    def insert_list(self, name, hotspot):
        sql = "INSERT INTO dailytb (name, hotspot) VALUES (%s, %s)"
        with self.connect() as con:
            try:
                with con.cursor() as cur:
                    cur.execute(sql, (name, hotspot))
                con.commit()
                return True
            except Exception:
                con.rollback()
                return False

    # 값 수정
    def update_list(self, id, name=None, hotspot=None):
        sql_first = "UPDATE dailytb SET "
        sql_last = " WHERE id=%s"

        set_clauses = []
        values = []

        if name:  # 빈 문자열은 False 취급됨
            set_clauses.append("name=%s")
            values.append(name)

        if hotspot:
            set_clauses.append("hotspot=%s")
            values.append(hotspot)

        if not set_clauses:  # 바꿀 게 없으면 종료
            return False

        sql = sql_first + ", ".join(set_clauses) + sql_last
        values.append(id)

        with self.connect() as con:
            try:
                with con.cursor() as cur:
                    cur.execute(sql, values)
                    affected = cur.rowcount  # 영향을 받은 행 수
                if affected == 0:
                    # id가 존재하지 않아 업데이트된 행이 없던 경우
                    con.rollback()
                    return False
                con.commit()
                return True
            except Exception as e:
                print("오류 코드>", e)
                con.rollback()
                return False

    def delete_list(self, id_or_hotspot):
        sql_id = "DELETE FROM dailytb WHERE id=%s"
        sql_id_to_hotspot = "SELECT hotspot FROM dailytb WHERE id=%s"
        sql_hotspot = "DELETE FROM dailytb WHERE hotspot=%s"

        with self.connect() as con:
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