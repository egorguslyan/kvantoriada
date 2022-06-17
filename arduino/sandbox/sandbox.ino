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

#define ARR_SIZE 256
#define GSR_TIME 5
#define ECG_TIME 20
#define BTN 5

struct module
{
    uint8_t pin : 5;
    uint8_t enabled : 1;
    volatile uint8_t buffer[ARR_SIZE];
    void setup()
    {
        pinMode(pin, INPUT);
    }
    void read()
    {
        if((buffer[0] != ARR_SIZE - 1) && enabled)
        {
            buffer[0]++;
            buffer[buffer[0]] = analogRead(pin);
        }
    }
    void pop(uint8_t *target)
    {
        memcpy(target, buffer, sizeof(uint8_t) * ARR_SIZE);
        buffer[0] = 0;
    }
};

struct
{
    uint16_t seconds0 : 9;
    uint16_t seconds1 : 9;
    uint8_t pin : 5;
    uint8_t not_pin : 5;
    volatile uint8_t state : 1;
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
            case 0: {
                control.seconds0 &= 0b111100000;
                control.seconds0 |= eepromData & 0b11111;
            } break;
            case 2: {
                control.seconds1 &= 0b111100000;
                control.seconds1 |= eepromData & 0b11111;
            } break;
            case 1: {
                control.seconds0 &= 0b000011111;
                control.seconds0 |= (eepromData & 0b1111) << 5;
                GSR.enabled = (eepromData & 0b10000) >> 4;
            } break;
            case 3: {
                control.seconds1 &= 0b000011111;
                control.seconds1 |= (eepromData & 0b1111) << 5;
                ECG.enabled = EEG.enabled = (eepromData & 0b10000) >> 4;
            } break;
        }
    }
    noInterrupts(); {
        TCCR1A = 0;
        TCCR1B = 0;
        TIMSK1 = (1 << TOIE1);
        TCCR1B |= (1 << CS10);
        // TCCR1B |= (1 << CS11);
    } interrupts();
    Serial.begin(9600);
    delay(10);
}

void loop()
{
    char S[10];
    static uint32_t timer0, timer1, timer2;
    volatile uint8_t gsr[ARR_SIZE], ecg[ARR_SIZE], eeg[ARR_SIZE];
    uint8_t i, btn, prevBtn;

    // Нагрузка
    if(millis() - timer0 > 100)
    {
        timer0 = millis();
        delay(50);
    } delay(5);

    if(millis() - timer1 > ((uint32_t)(control.state ? control.seconds0 : control.seconds1) * 1000))
    {
        timer1 = millis();
        control.toggle();
    }

    control.enabled = GSR.enabled = ECG.enabled = EEG.enabled
        = !(millis() - timer2 > ((uint32_t)(control.seconds0 + control.seconds1) * 1000));
    if(!control.enabled)
        control.disable();

    btn = digitalRead(BTN);
    if(btn && !prevBtn)
        timer1 = timer2 = millis();
    prevBtn = btn;

    GSR.pop(gsr);
    ECG.pop(ecg);
    EEG.pop(eeg);
    shiftOut(11, 11, 0, gsr[0]);    // volatile didn't help
    shiftOut(11, 11, 0, ecg[0]);
    shiftOut(11, 11, 0, eeg[0]);
    if(control.state)
        for(i = 1; i <= gsr[0]; i++)
        {
            sprintf(S, "%d %d %d", 0, 0, gsr[i]);
            Serial.println(S);
        }
    else
        for(i = 1; i <= ecg[0]; i++)
        {
            sprintf(S, "%d %d %d", ecg[i], eeg[i], 0);
            Serial.println(S);
        }
    gsr[0] = ecg[0] = eeg[0] = 0;
}

ISR(TIMER1_OVF_vect)
{
    intr_counter++;
    if(intr_counter >= 10)
    {
        intr_counter = 0;
        digitalWrite(13, HIGH);
        if(control.enabled)
        {
            if(control.state)
                GSR.read();
            else
            {
                ECG.read();
                EEG.read();
            }
        }
        digitalWrite(13, LOW);
    }
}