#define TIME 15
#define NUM 200L * TIME
#define SIZE 16

#define PINEKG A1
#define PINGSR A2
#define GNDEKG 11
#define GNDGSR A0
#define PINBTN 9
#define PINLED 3

#include <SoftwareSerial.h>
#include <GyverOLED.h>

GyverOLED<SSD1306_128x32, OLED_BUFFER> oled;

SoftwareSerial mySerial(8, 7); // RX, TX

void setup()
{
  Serial.begin(9600);
  mySerial.begin(38400);

  pinMode(GNDEKG, 1);
  pinMode(GNDGSR, 1);
  digitalWrite(GNDEKG, 1);
  digitalWrite(GNDGSR, 0);

  oled.init();
  Wire.setClock(800000L);
  oled.clear();

  pinMode(PINBTN, INPUT);
  pinMode(PINLED, OUTPUT);
}

int y0;

void plotter(int y) {
  for (int j=0; j<4; j++) {
    for (int i=0; i<127; i++) {
      oled._oled_buffer[j+i*4]=oled._oled_buffer[j+i*4+4];
    }
    oled._oled_buffer[j+127*4]=0;
  }
  //y = analogRead(A1);
  //Serial.println(y);
  y = 16.0 * y / analogRead(A6); // верхний потенциометр - аттенюатор
  //oled._oled_buffer[y/8 + 127*4]=1<<(y%8);
  oled.line(126,y0+(analogRead(A7)-512)/8,127,y+(analogRead(A7)-512)/8); // нижний потенциометр - смещение
  y0=y;
  oled.update();
}

int data;

void loop()
{
  delay(300);
  digitalWrite(PINLED, LOW);
  while (digitalRead(PINBTN) == LOW) {
    data = analogRead(PINEKG);
    plotter(1023 - data);
  }

  // delay(300);
  digitalWrite(PINLED, HIGH);
  mySerial.write(255);
  for (long i = 0 ; i < NUM; i++) {
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