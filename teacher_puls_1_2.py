import serial
import time
import threading
import re
import mysql.connector
from datetime import date

read_data = ""
today = date.today()

def thread_task():
    global read_data
    while True:
        try:
            local_data = ser.readline()
            if local_data:
                decoded = local_data.decode('utf-8', errors='ignore')
                read_data += decoded
                
        except Exception as e:
            print("⚠️ 디코딩 오류:", e)

try:
    ser = serial.Serial('COM3', 9600, timeout=2) #포트 확인
    time.sleep(2)
    
except:
    print("❌ 시리얼 포트 연결 실패")
    exit()


my_thread = threading.Thread(target=thread_task)
my_thread.daemon = True
my_thread.start()


conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='shcho8783@', # ← 실제 비밀번호로 변경
    database='products'    # ← 실제 DB 이름으로 변경
)
cursor = conn.cursor()

read_data = ""
ser.write('AT+CWLAP\r\n'.encode('utf-8'))
print("AT+CWLAP 명령 전송됨")
time.sleep(3)

ssids = re.findall(r'\+CWLAP:\(\d+,"(.*?)"', read_data)

for ssid in ssids:
    
    cursor.execute("SELECT id FROM dailytb WHERE hotspot_name = %s", (ssid,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE dailytb SET daily_score = daily_score + 1 WHERE hotspot_name = %s", (ssid,))
        print(f"SSID '{ssid}' 존재 → daily_score 증가")
    else:
        print(f"SSID '{ssid}' 없음 → 업데이트 생략")

conn.commit()

# 오늘 날짜
today = date.today()

# 날짜 비교 및 초기화
cursor.execute("SELECT MAX(last_reset_date) FROM dailytb")
last_reset = cursor.fetchone()[0]

if last_reset != today:
    cursor.execute("UPDATE dailytb SET daily_score = 0, last_reset_date = %s", (today,))
    print("날짜 변경 감지 → daily_score 초기화 완료")
else:
    print("오늘 이미 초기화됨 → 초기화 생략")


ser.write(b'stop\n')
print("stop 명령 전송됨")
time.sleep(2)

cursor.close()
conn.close()
ser.close()
print("✅ 모든 작업 완료")