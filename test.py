import mysql.connector

config = dict(
    host='localhost',
    user='root',
    password='123',
    database='attenddb',
    charset='utf8'
)

try:
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()

    cur.execute("SELECT period, time FROM timetable ORDER BY period")
    rows = cur.fetchall()

    print("저장된 시간표:")
    for period, time in rows:
        print(f"{period}교시: {time}")

except mysql.connector.Error as e:
    print("DB 오류 발생:", e)

finally:
    try:
        if conn:
            conn.close()
    except NameError:
        pass