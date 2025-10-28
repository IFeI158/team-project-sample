import pymysql
DB_CONFIG = dict(
    host = "localhost",
    user = "root" ,
    password="123",
    database="sampledb",
    charset="utf8"
)

class DB:
    def __init__(self,**config):
        self.config = config
    
    def connect(self):
        return pymysql.connect(**self.config) #딕셔너리 전개
    
    #로그인 검증
    def verify_user(self, username, password):
        sql = "SELECT COUNT(*) FROM users WHERE username=%s AND password=%s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql,(username, password))
                count, = cur.fetchone()
                return count == 1
            
    #멤버 전체 조회
    def fetch_members(self):
        sql = "SELECT id, name, email FROM members ORDER BY id"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall() #[(id, name, email), ...]
            
    #멤버 추가
    def insert_member(self, name, email):
        sql = "INSERT INTO MEMBERS (name, email) VALUES(%s,%s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql,(name,email))
                    conn.commit()
                    return True
            except Exception:
                conn.rollback()
                return False
            
    # 멤버 삭제
    def delete_member(self, name, email):
        sql = "DELETE FROM MEMBERS WHERE name = %s AND email = %s"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (name, email))
                    conn.commit()
                    return True
            except Exception:
                conn.rollback()
                return False