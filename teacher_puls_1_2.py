import serial
import time
import threading
import re
from stu_connect import DB, config

db = DB(**config)
conn = db.connect()
cursor = conn.cursor()

read_data = ""
stop_thread = False  # 종료 플래그

def thread_task():
    global read_data
    while not stop_thread:
        try:
            if ser and ser.is_open:
                local_data = ser.readline()
                if local_data:
                    decoded = local_data.decode('utf-8', errors='ignore')
                    read_data += decoded
            else:
                break
        except Exception as e:
            # 포트 닫힘 이후 발생하는 오류는 무시
            if "port that is not open" not in str(e):
                print("⚠️ 디코딩 오류:", e)
            break  # 스레드 종료

try:
    ser = serial.Serial('COM5', 9600, timeout=2)
    time.sleep(2)
except Exception as e:
    print("❌ 시리얼 포트 연결 실패:", e)
    exit()

my_thread = threading.Thread(target=thread_task)
my_thread.start()

# --- 메인 로직 ---
read_data = ""
ser.write(b'AT+CWLAP\r\n')
print("AT+CWLAP 명령 전송됨")
time.sleep(5)

ssids = re.findall(r'\+CWLAP:\(\d+,"(.*?)"', read_data)

for ssid in ssids:
    cursor.execute("SELECT id FROM dailytb WHERE hotspot = %s", (ssid,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE dailytb SET daily_score = daily_score + 1 WHERE hotspot = %s", (ssid,))
        print(f"SSID '{ssid}' 존재 → daily_score 증가")
    else:
        print(f"SSID '{ssid}' 없음 → 업데이트 생략")

conn.commit()

ser.write(b'stop\n')
print("stop 명령 전송됨")
time.sleep(2)

# --- 안전 종료 ---
stop_thread = True
time.sleep(0.5)
if ser.is_open:
    ser.close()

cursor.close()
conn.close()
print("✅ 모든 작업 완료")
