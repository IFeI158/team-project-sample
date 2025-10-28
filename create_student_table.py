import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "000630",
    "charset": "utf8",
    "database": "sampledb"
}

create_table_sql = """
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    hotspot VARCHAR(50) NOT NULL,
    daily_score INT DEFAULT 0
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
