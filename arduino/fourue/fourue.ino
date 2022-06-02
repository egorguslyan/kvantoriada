#define NUM 256
#define SIZE 16
#define PINEKG A1
#define PINGSR A2
#define GNDEKG 11
#define GNDGSR A0

#include <SoftwareSerial.h>

SoftwareSerial mySerial(8, 7); // RX, TX
int data;

void setup()
{
  mySerial.begin(38400);
  pinMode(GNDEKG, 1);
  pinMode(GNDGSR, 1);
  digitalWrite(GNDEKG, 1);
  digitalWrite(GNDGSR, 0);
}

void loop()
{
  // delay(300);
  mySerial.write(255);
  for (int i = 0 ; i < NUM; i++) {
    data = analogRead(PINEKG);
    mySerial.write(map(data, 0, 1024, 0, 254));
    delay(5);
  }
  /*
  digitalWrite(GNDEKG, 0);
  digitalWrite(GNDGSR, 1);
  mySerial.write(254);
  delay(400);
  for (int i = 0 ; i < 8; i++) {
    data = analogRead(PINGSR);
    for (int j = 0; j < NUM / 8; ++j)
      mySerial.write(map(data, 0, 1024, 0, 255));
    delay(10);
  }
  digitalWrite(GNDEKG, 1);
  digitalWrite(GNDGSR, 0);
  */
}