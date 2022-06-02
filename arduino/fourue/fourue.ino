#define NUM 256
#define PINEKG A1
#define PINGSR A2
#define GNDEKG 11
#define GNDGSR A0

#include <SoftwareSerial.h>

SoftwareSerial mySerial(8, 7); // RX, TX

byte inputEKG[NUM];
byte inputGSR[NUM];
int data;

void setup()
{
  Serial.begin(9600);
  mySerial.begin(38400);
  pinMode(GNDEKG, 1);
  pinMode(GNDGSR, 1);
  digitalWrite(GNDEKG, 1);
  digitalWrite(GNDGSR, 0);
}

void loop()
{
  //uint32_t ti = millis();
  delay(300);
  for (int i = 0 ; i < NUM; i++) {
    data = analogRead(PINEKG);
    inputEKG[i] = map(data, 0, 1024, 0, 255);
    delay(5);
  }
  digitalWrite(GNDEKG, 0);
  digitalWrite(GNDGSR, 1);
  delay(400);
  for (int i = 0 ; i < 8; i++) {
    data = analogRead(PINGSR);
    inputGSR[i] = map(data, 0, 1024, 0, 255);
    delay(10);
  }
  digitalWrite(GNDEKG, 1);
  digitalWrite(GNDGSR, 0);
  //uint16_t rate  = (uint16_t)NUM * 500 / (millis() - ti);
  //Serial.println(millis()-ti);
  //uint32_t tim = millis();
  mySerial.write(255);
  //mySerial.write(rate);
  for (int i = 0; i < NUM; i++) {
    mySerial.write(inputEKG[i]);
  }

  for (int i = 0; i < NUM; i++) {

    mySerial.write(inputGSR[int(i/32)]);
  }
  //Serial.println(millis()-tim);
}