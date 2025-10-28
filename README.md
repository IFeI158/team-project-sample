bell.py (아두이노 실행용 모듈 사용 설명은 코드 내에)

--------------------------------------------------------------------------

#include <SoftwareSerial.h>
SoftwareSerial espSerial(2, 3); // RX, TX

int buzzer = 11;

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
      playMelody();
    }else{
      espSerial.println(cmd);
    }
  }

  if (espSerial.available()) {
    String resp = espSerial.readStringUntil('\n');
    Serial.println(resp);
  }

  // if (Serial.available() > 0) {
  //   char cmd = Serial.read();
  //   if (cmd == 'P') { // Python에서 'P' 보내면 재생
  //     playMelody();}}
}


void playMelody() {
  // 🎵 미 도 레 솔
  tone(buzzer, 659, 500); // 미 (E5)
  delay(550);
  tone(buzzer, 523, 500); // 도 (C5)
  delay(550);
  tone(buzzer, 587, 500); // 레 (D5)
  delay(550);
  tone(buzzer, 392, 800); // 낮은 솔 (G4)
  delay(1000);

  // 🎵 솔 레 미 도
  tone(buzzer, 392, 500); // 낮은 솔 (G4)
  delay(550);
  tone(buzzer, 587, 500); // 레 (D5)
  delay(550);
  tone(buzzer, 659, 500); // 미 (E5)
  delay(550);
  tone(buzzer, 523, 800); // 도 (C5)
  delay(900);

  noTone(buzzer);
}

