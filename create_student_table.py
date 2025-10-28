import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123",
    "charset": "utf8",
    "database": "sampledb"
}

create_table_sql = """
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    `1` INT DEFAULT 0,
    `2` INT DEFAULT 0,
    `3` INT DEFAULT 0,
    `4` INT DEFAULT 0,
    `5` INT DEFAULT 0,
    `6` INT DEFAULT 0,
    `7` INT DEFAULT 0,
    `8` INT DEFAULT 0,
    total INT AS (`1`+`2`+`3`+`4`+`5`+`6`+`7`+`8`) STORED
);
"""

try:
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
    conn.commit()
    print("✅ students 테이블 수정 완료")
except Exception as e:
    print("❌ 실패:", e)
finally:
    conn.close()
