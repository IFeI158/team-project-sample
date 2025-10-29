import time
import mysql.connector
from datetime import datetime
import subprocess

def run_teacher_puls_1_2_task():
    subprocess.run(["python", "teacher_puls_1_2"])  

def check_schedule_and_run():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='shcho8783@', # ← 실제 비밀번호로 변경
        database='products'    # ← 실제 데이터베이스로 변경
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM schedule_table
        WHERE start_time = %s OR end_time = %s
    """, (now, now))  #실제 파일, 테이블명
    rows = cursor.fetchall()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    for row in rows:
        run_time = row[0].strftime('%Y-%m-%d %H:%M')
        if run_time == now:
            print(f"{run_time}에 실행 시작")
            run_teacher_puls_1_2_task()

    cursor.close()
    conn.close()

while True:
    check_schedule_and_run()
    time.sleep(60)  # 1분마다 체크