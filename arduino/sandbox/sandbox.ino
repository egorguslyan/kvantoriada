#define DEBUG_LED 13
#define BTN 5

/* После изменения стандартных значений времени
   нужно обязательно запустить gen.bat или gen.sh */
#define GSR_TIME 5
#define ECG_TIME 10

#include <EEPROM.h>
/*    Mem map    **
    0) GSR1
    1) GSR2
    2) E*G1
    3) E*G2
**               */

#if __has_include("random_key.h")
    #include "random_key.h"
#else
    #error "Сгенерируйте ключ с помощью gen.bat или gen.sh"
#endif

#define GSR_T ((uint32_t)control.seconds0 * 1000)
#define ECG_T ((uint32_t)control.seconds1 * 1000)

struct module
{
    uint8_t pin : 5;
    uint8_t enabled : 1;
    void setup()
    {
        pinMode(pin, INPUT);
    }
    uint8_t read()
    {
        return enabled ? analogRead(pin) : 0;
    }
};

struct
{
    uint16_t seconds0 : 9;
    uint16_t seconds1 : 9;
    uint8_t pin : 5;
    uint8_t not_pin : 5;
    uint8_t state : 1;
    uint8_t enabled : 1;
    void updpins()
    {
        enabled = 1;
        digitalWrite(pin, state);
        digitalWrite(not_pin, !state);
    }
    void setup()
    {
        pinMode(pin, OUTPUT);
        pinMode(not_pin, OUTPUT);
        updpins();
    }
    void set(uint8_t s)
    {
        state = s;
        updpins();
    }
    void toggle()
    {
        if(enabled)
        {
            state = !state;
            updpins();
        }
    }
    void disable()
    {
        enabled = 0;
        digitalWrite(pin, LOW);
        digitalWrite(not_pin, LOW);
    }
} control;

enum
{
    SER_GSR = 'G',
    SER_ECG = 'C',
    SER_EEG = 'E',
};
const char SERKEYS[3] = {SER_GSR, SER_ECG, SER_EEG};

module GSR;
module ECG;
module EEG;

uint8_t intr_counter;

uint8_t eeprom_byte_check(uint8_t b, uint8_t useful_bits)
{
    uint8_t m, i;
    m = 0b01111111 & (0b11111111 << useful_bits);
    if((eeprom_key & m) != (b & m))
        return EXIT_FAILURE;
    m = 0;
    for(i = 0; i < 7; i++)
        m ^= bitRead(b, i);
    if(m != bitRead(b, 7))
        return EXIT_FAILURE;
    return EXIT_SUCCESS;
}

uint8_t eeprom_byte_form(uint8_t b, uint8_t useful_bits)
{
    uint8_t r, m, i;
    m = 0b11111111 << useful_bits;
    r = (eeprom_key & m) + (b & (m ^ 0b11111111));
    m = 0;
    for(i = 0; i < 7; i++)
        m ^= bitRead(r, i);
    bitWrite(r, 7, m);
    return r;
}

extern volatile unsigned long timer0_millis;

void setup()
{
    uint8_t eepromData, i;
    pinMode(BTN, INPUT);
    pinMode(13, OUTPUT);
    control.pin = A3;
    control.not_pin = 12;
    control.setup();
    control.disable();
    GSR.pin = A2;
    GSR.setup();
    ECG.pin = A1;
    ECG.setup();
    EEG.pin = A0;
    EEG.setup();
    control.seconds0 = control.seconds1 = 0;
    for(i = 0; i < 4; i++)
    {
        eepromData = EEPROM.read(i);
        if(eeprom_byte_check(eepromData, 5))
        {
            if(i < 4)
            {
                if(i % 2)
                {
                    eepromData = eeprom_byte_form(
                        ((i / 2) ? ECG_TIME : GSR_TIME) & 0b11111,
                        5
                    );
                }
                else
                {
                    eepromData = eeprom_byte_form(
                        ((((i / 2) ? ECG_TIME : GSR_TIME) >> 5) & 0b1111) + (1 << 4),
                        5
                    );
                }
            }
            EEPROM.write(i, eepromData);
        }
        switch(i)
        {
            case 1: {
                control.seconds0 &= 0b111100000;
                control.seconds0 |= eepromData & 0b11111;
            } break;
            case 3: {
                control.seconds1 &= 0b111100000;
                control.seconds1 |= eepromData & 0b11111;
            } break;
            case 0: {
                control.seconds0 &= 0b000011111;
                control.seconds0 |= (eepromData & 0b1111) << 5;
                GSR.enabled = (eepromData & 0b10000) >> 4;
            } break;
            case 2: {
                control.seconds1 &= 0b000011111;
                control.seconds1 |= (eepromData & 0b1111) << 5;
                ECG.enabled = EEG.enabled = (eepromData & 0b10000) >> 4;
            } break;
        }
    }
    noInterrupts();
    timer0_millis = GSR_T + ECG_T;
    interrupts();
    Serial.begin(38400);
    control.disable();
    GSR.enabled =
    ECG.enabled =
    EEG.enabled = 0;
    delay(10);
}

void loop()
{
    char S[10];
    static uint32_t timer0 = 0, timer1 = 0, timer2 = 0, timer3 = 0;
    uint8_t gsr, ecg, eeg;
    const uint8_t *mod[3] = {&gsr, &ecg, &eeg};
    uint8_t i, btn, prevBtn;

    // Нагрузка
    // if(millis() - timer0 > 100)
    // {
    //     timer0 = millis();
    //     delay(50);
    // } delay(5);

    if(millis() - timer1 > (control.state ? GSR_T : ECG_T))
    {
        timer1 = millis();
        control.toggle();
    }

    control.enabled = !(millis() - timer2 > (GSR_T + ECG_T));
    if(!control.enabled)
    {
        if(GSR.enabled || ECG.enabled || EEG.enabled)
            Serial.print('f');
        control.disable();
        GSR.enabled =
        ECG.enabled =
        EEG.enabled = 0;
    }
    else
    {
        GSR.enabled = control.state;
        ECG.enabled = !control.state;
        EEG.enabled = !control.state;
    }

    btn = digitalRead(BTN);
    if(btn && !prevBtn)
            timer1 = timer2 = millis();
    prevBtn = btn;

    if(millis() - timer3 > 5)
    {
        timer3 = millis();
        digitalWrite(13, HIGH);
        gsr = GSR.read();
        ecg = ECG.read();
        eeg = EEG.read();
        digitalWrite(13, LOW);
    }

    for(i = 0; i < 3; i++)
        if(*mod[i] != 0)
        {
            Serial.print(SERKEYS[i]);
            Serial.print(*mod[i]);
            Serial.print(';');
        }
}