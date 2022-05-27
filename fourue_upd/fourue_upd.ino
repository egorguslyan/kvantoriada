#define NUM 16
#define PINEKG A1
#define PINGSR A2
#define GNDEKG A0
#define GNDGSR 11


#include <SoftwareSerial.h>

SoftwareSerial mySerial(8, 7); // RX, TX

byte inputEKG[NUM];
byte inputGSR[NUM];

void setup()
{
  Serial.begin(9600);
  mySerial.begin(38400);
  pinMode(GNDEKG, 1);
  pinMode(GNDGSR, 1);
}

void loop()
{
  uint32_t ti = millis();
  for (int i = 0 ; i < NUM; i++) {
    digitalWrite(GNDEKG, 1);
    digitalWrite(GNDGSR, 0);
    delay(3);
    int data = analogRead(PINEKG);
    inputEKG[i] = map(data, 0, 1024, 0, 255);
    digitalWrite(GNDEKG, 0);
    digitalWrite(GNDGSR, 1);
    delay(3);
    data = analogRead(PINGSR);
    inputGSR[i] = map(data, 0, 1024, 0, 255);
  }
  
  digitalWrite(11, 0);
  uint16_t rate  = (uint16_t)NUM * 1000 / (millis() - ti);
  mySerial.write(255);
  //mySerial.write(rate);
  for (int i = 0; i < NUM; i++) {
    mySerial.write(inputEKG[i]);
  }

  for (int i = 0; i < NUM; i++) {
    mySerial.write(inputGSR[i]);
  }
}
