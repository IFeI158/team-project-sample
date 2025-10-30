import serial
import time
import threading
import re
import mysql.connector


class WifiChecker:
    def __init__(self, port='COM5', baudrate=9600, db_config=None):
        self.read_data = ""
        self.ser = None
        self.thread = None

        # DB 연결 정보
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '000630',
            'database': 'attenddb'
        }

        # 시리얼 초기화
        try:
            self.ser = serial.Serial(port, baudrate, timeout=2)
            time.sleep(2)
            print(f"✅ 시리얼 포트 {port} 연결 성공")
        except Exception as e:
            print("❌ 시리얼 포트 연결 실패:", e)
            raise

        # 수신 스레드 시작
        self.thread = threading.Thread(target=self._read_thread)
        self.thread.daemon = True
        self.thread.start()

    def _read_thread(self):
        """시리얼에서 데이터 계속 읽기"""
        while True:
            try:
                local_data = self.ser.readline()
                if local_data:
                    decoded = local_data.decode('utf-8', errors='ignore')
                    self.read_data += decoded
                    print(decoded, end="")
            except Exception as e:
                print("⚠️ 디코딩 오류:", e)

    def scan_wifi(self):
        """Wi-Fi 스캔 명령 전송 후 SSID 목록 추출"""
        self.read_data = ""
        self.ser.write('AT+CWLAP\r\n'.encode('utf-8'))
        print("📡 AT+CWLAP 명령 전송됨")

        time.sleep(3)
        ssids = re.findall(r'\+CWLAP:\(\d+,"(.*?)"', self.read_data)
        print("🔍 검색된 SSID:", ssids)
        return ssids

    def update_db(self, ssids):
        """SSID가 DB에 있으면 daily_score 증가"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            for ssid in ssids:
                cursor.execute("SELECT id FROM dailytb WHERE hotspot_name = %s", (ssid,))
                result = cursor.fetchone()

                if result:
                    cursor.execute(
                        "UPDATE dailytb SET daily_score = daily_score + 1 WHERE hotspot_name = %s",
                        (ssid,)
                    )
                    print(f"✅ SSID '{ssid}' 존재 → daily_score +1")
                else:
                    print(f"⚠️ SSID '{ssid}' 없음 → 업데이트 생략")

            conn.commit()
            cursor.close()
            conn.close()
            print("💾 DB 업데이트 완료")

        except Exception as e:
            print("❌ DB 작업 실패:", e)

    def stop(self):
        """시리얼 및 스레드 종료"""
        if self.ser and self.ser.is_open:
            self.ser.write(b'stop\n')
            print("🛑 stop 명령 전송됨")
            time.sleep(1)
            self.ser.close()
            print("🔌 시리얼 포트 닫힘")


# -----------------------------
# 테스트용 실행 (직접 실행할 때만 작동)
# -----------------------------
if __name__ == "__main__":
    checker = WifiChecker()

    ssid_list = checker.scan_wifi()
    checker.update_db(ssid_list)
    checker.stop()
    print("✅ 모든 작업 완료")
