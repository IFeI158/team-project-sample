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

def bell_on():
    script_path = os.path.join(os.getcwd(), "bellon.py")
    
    try:
        subprocess.run([sys.executable, script_path])
        print(f"[실행 완료] {script_path}")
    except Exception as e:
        print(f"❌ bellon.py 실행 오류: {e}")

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
        SELECT start_time, end_time, period 
        FROM timetable
        WHERE start_time = %s OR end_time = %s
    """, (now, now))

    rows = cursor.fetchall()

    for row in rows:
        start_time = str(row[0])[:5] if row[0] else None
        end_time   = str(row[1])[:5] if row[1] else None
        current_period = row[2]

        if now == start_time:
            print(f"⏰ {now} → teacher_puls_1_2.py 실행")
            run_teacher_puls_1_2_task()

        if now == end_time:
            print(f"⏰ {now} → 종소리 울려라")
            bell_on()

            # 마지막 교시인지 판단
            cursor.execute("SELECT MAX(period) FROM timetable")
            last_period = cursor.fetchone()[0]

            if current_period == last_period:
                print("마지막 교시입니다. 집으로 꺼지세요! 😆")
            else:
                print("다음 수업 준비하세요~")


        cursor.close()
        conn.close()

# 메인 루프 (1분마다 체크)
print("⏳ 자동 실행 스케줄러 시작... (60초 간격 체크)")
while True:
    check_schedule_and_run()
    time.sleep(60)