bell.py (아두이노 실행용 모듈 사용 설명은 코드 내에)

--------------------------------------------------------------------------

#include <SoftwareSerial.h>
SoftwareSerial espSerial(2, 3); // RX, TX

int buzzer = 11;

// 🎵 두 번째 코드 멜로디 & 박자
int melody[] = {
  262, 392, 523, 659, 784, 1047, 1319,
  1175, 1175, 1047, 1047, 988, 880, 880,
  196, 247, 294, 392, 494, 587, 988,
  880, 880, 784, 784, 698, 659, 659,
  262, 392, 523, 659, 784, 1047, 1319,
  1175, 1175, 1047, 1047, 988, 880, 880,
  196, 247, 294, 349, 494, 587,
  262, 330, 392, 523, 659, 784,
  392, 440, 392, 349, 392, 659, 587, 523
};

int noteDurations[] = {
  300,200,200,300,200,200,450,
  100,300,100,300,200,100,350,
  300,200,200,300,200,200,450,
  100,300,100,300,200,100,350,
  300,200,200,300,200,200,450,
  100,300,100,300,200,100,350,
  200,200,200,200,200,200,
  200,200,200,200,200,200,
  250,100,150,100,150,350,100,500
};

void setup() {
  pinMode(buzzer, OUTPUT);
  Serial.begin(9600);
  espSerial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');

    if(cmd == "stop"){
      Serial.println("stop을 누르셨습니다!");
      playMelody();  // ✅ melody 배열 기반 재생
    }else{
      espSerial.println(cmd);
    }
  }

  if (espSerial.available()) {
    String resp = espSerial.readStringUntil('\n');
    Serial.println(resp);
  }
}

// 🎵 melody 배열과 noteDurations 배열 기반 재생
void playMelody() {
  int length = sizeof(melody)/sizeof(int);

  for (int i = 0; i < length; i++) {
    tone(buzzer, melody[i], noteDurations[i]);
    delay(noteDurations[i] + 50); // 각 음 사이 약간 여유
  }
  noTone(buzzer); // 재생 종료
}

