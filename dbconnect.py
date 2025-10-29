import pymysql

config = dict(
    host = 'localhost',
    user = 'root',
    password = '123',        # SQL workspace 개인 비밀번호로 변경
    database = 'attenddb',
    charset = 'utf8'
)

class DB:
    def __init__(self, **CONFIG):
        self.config = CONFIG

    def connect(self):
        return pymysql.connect(**self.config)