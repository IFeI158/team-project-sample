import threading
import serial
import serial.tools.list_ports
import time

serial_receive_data = ""
def serial_read_thread():
    global serial_receive_data
    while True:
        serial_receive_data = my_serial.readline().decode()

def main():
    try:
        global serial_receive_data
        while True:
            if serial_receive_data : 
                print(serial_receive_data)
                serial_receive_data = ""
    except KeyboardInterrupt:
        pass

# 별도 포트 확인 필요 없이 아두이노 연결된 포트 찾음. 단점은 연산이 많아져서 오래걸린다?
if __name__ == 'unoconnect':
    
    ports = list(serial.tools.list_ports.comports())
    # .comports() : 현재 연결된 모든 포트를 다 가져와서 확인

    for p in ports:
        if 'Arduino Uno' in p.description:
            print(f"{p} 포트에 연결하였습니다.")
            my_serial = serial.Serial(p.device, baudrate=9600, timeout=1.0)
            time.sleep(2.0)

    t1 = threading.Thread(target=serial_read_thread)
    t1.daemon = True
    t1.start()
    
    main()