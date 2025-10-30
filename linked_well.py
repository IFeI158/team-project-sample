import time
import mysql.connector
from datetime import datetime, timedelta
import subprocess
import os
import sys

from month_table import move_daily_to_month

# 중복 방지용
last_executed_times = set()

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

def timedelta_to_str(td):
    if not td:
        return None
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def check_schedule_and_run():
    global last_executed_times
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123',
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
    """)
    rows = cursor.fetchall()

    for row in rows:
        start_time = timedelta_to_str(row[0])
        end_time   = timedelta_to_str(row[1])
        current_period = row[2]

        # 디버깅용
        print(f"[DEBUG] now={now}, start={start_time}, end={end_time}")

        # 중복 방지 로직
        if now == start_time and f"start_{current_period}_{now}" not in last_executed_times:
            print(f"⏰ {now} → teacher_puls_1_2.py 실행")
            run_teacher_puls_1_2_task()
            last_executed_times.add(f"start_{current_period}_{now}")

        if now == end_time and f"end_{current_period}_{now}" not in last_executed_times:
            print(f"⏰ {now} → 종소리 울려라")
            bell_on()
            last_executed_times.add(f"end_{current_period}_{now}")

            # 마지막 교시 확인
            cursor.execute("SELECT MAX(period) FROM timetable")
            last_period = cursor.fetchone()[0]

            if current_period == last_period:
                print("마지막 교시가 끝났습니다. 집으로 가세요! 😆\n시스템 정산 시작 ...")
                move_daily_to_month(1)
                print("시스템 정산 완료")

    cursor.close()
    conn.close()


print("⏳ 자동 실행 스케줄러 시작... (10초 간격 체크)")
while True:
    check_schedule_and_run()
    time.sleep(10)
