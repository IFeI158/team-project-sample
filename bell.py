import serial
import time

def bell_on(port='COM3', baudrate=9600):
    try:
        arduino = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # 아두이노 초기화 대기
        arduino.write(b'P')  # 벨 신호 전송
    except Exception as e:
        print("⚠️ Bell signal failed:", e)
    finally:
        try:
            arduino.close()
        except:
            pass


'''
import bell
bell.bell_on() 으로 사용
'''