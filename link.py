import time
import mysql.connector
from datetime import datetime
import subprocess
import os
import sys
from month_table import move_daily_to_month

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

def timedelta_to_str(td):
    """datetime.timedelta → 'HH:MM' 문자열로 변환"""
    if not td:
        return None
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


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
<<<<<<< HEAD
        start_time = timedelta_to_str(row[0])
        end_time   = timedelta_to_str(row[1])
        current_period = row[2]

        print(f"[DEBUG] 비교 → now={now}, start={start_time}, end={end_time}")

=======
        start_time = str(row[0])[:5] if row[0] else None
        end_time   = str(row[1])[:5] if row[1] else None
        current_period = row[2]

>>>>>>> 7c4d5ab3504bc7a8af07923865150bf45a8443a1
        if now == start_time:
            print(f"⏰ {now} → teacher_puls_1_2.py 실행")
            run_teacher_puls_1_2_task()

        if now == end_time:
            print(f"⏰ {now} → 종소리 울려라")
            bell_on()

<<<<<<< HEAD

=======
>>>>>>> 7c4d5ab3504bc7a8af07923865150bf45a8443a1
            # 마지막 교시인지 판단
            cursor.execute("SELECT MAX(period) FROM timetable")
            last_period = cursor.fetchone()[0]

            if current_period == last_period:
                print("마지막 교시가 끝났습니다. 집으로 가세요! 😆\n시스템 정산 시작 ...")
<<<<<<< HEAD
                move_daily_to_month(1)
                print("시스템 정산 완료")
=======
                move_daily_to_month(datetime.now().day)
>>>>>>> 7c4d5ab3504bc7a8af07923865150bf45a8443a1



    cursor.close()
    conn.close()

# 메인 루프 (1분마다 체크)
print("⏳ 자동 실행 스케줄러 시작... (60초 간격 체크)")
while True:
    check_schedule_and_run()
    time.sleep(10)