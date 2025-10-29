import time
import mysql.connector
from datetime import datetime
import subprocess
import os
import sys

# teacher_puls_1_2.py 실행 함수
def run_teacher_puls_1_2_task():
    script_path = os.path.join(os.getcwd(), "teacher_puls_1_2.py")
    
    try:
        subprocess.run([sys.executable, script_path])
        print(f"[실행 완료] {script_path}")
    except Exception as e:
        print(f"❌ teacher_puls_1_2.py 실행 오류: {e}")

# DB 스케줄 확인 함수
def check_schedule_and_run():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123',  # ← DB 비밀번호
            database='attenddb'
        )
        cursor = conn.cursor()
    except Exception as e:
        print("❌ DB 접속 오류:", e)
        return
    
    now = datetime.now().strftime('%H:%M')

    cursor.execute("""
        SELECT start_time, end_time 
        FROM timetable
        WHERE start_time = %s OR end_time = %s
    """, (now, now))

    rows = cursor.fetchall()

    for row in rows:
        start_time = str(row[0])[:5] if row[0] else None   # "HH:MM" 추출
        end_time   = str(row[1])[:5] if row[1] else None


        # 현재 시간이 수업 시작 or 종료 시간과 일치하면 실행
        if now == start_time or now == end_time:
            print(f"⏰ {now} → teacher_puls_1_2.py 실행")
            run_teacher_puls_1_2_task()

    cursor.close()
    conn.close()

# 메인 루프 (1분마다 체크)
print("⏳ 자동 실행 스케줄러 시작... (10초 간격 체크)")
while True:
    check_schedule_and_run()
    time.sleep(10)
