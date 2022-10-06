// Состояние Bluetooth
#define BLUETOOTH_ENABLE 1
// Светодиод отладки
#define DEBUG_LED 13
// Кнопка начала измерений
#define BTN0 5
// Индикационные светодиоды
#define LEDW 2
#define LEDY 3
#define LEDR 4
// Аттеньюаторы
#define P0 A6
#define P1 A7

// Время измерения для каждого датчика (выставляется в программе)
#define GSR_TIME 5
#define ECG_TIME 10
#define EEG_TIME 15

#include <EEPROM.h>
#define eeprom_key ((uint8_t) __TIME__ & 127)
/*    Mem map    **
    0) TIMG
    1) E*TG
    2) TIMC
    3) E*TC
    4) TIME
    5) E*TE
**               */

#include <GyverOLED.h>
GyverOLED<SSD1306_128x32, OLED_BUFFER> oled;

#if(BLUETOOTH_ENABLE)
#include <SoftwareSerial.h>
SoftwareSerial serial(8, 7);
#else
#define serial Serial
#endif

#define max(a, b) ((a) > (b) ? (a) : (b))

#define GSR_T (control.enabled0 ? ((uint32_t)control.seconds0 * 1000) : 0)
#define ECG_T (control.enabled1 ? ((uint32_t)control.seconds1 * 1000) : 0)
#define EEG_T (control.enabled2 ? ((uint32_t)control.seconds2 * 1000) : 0)
#define E_T (max(ECG_T, EEG_T))

/* Структура для измерительных модулей.
 * Раньше здесь был буффер, теперь же
 * она почти бесполезна */
struct module
{
    uint8_t pin : 5;
    uint8_t enabled : 1;
    void setup()
    {
        pinMode(pin, INPUT);
        enabled = 0;
    }
    uint16_t read()
    {
        return analogRead(pin);
    }
};

/* Структура, управляющая модулями.
 * Переключает конфликтующие группы модулей:
 * 1: ECG, EEG;
 * 2: GSR.
 * Есть возможность отключить всё.*/
struct
{
    uint16_t seconds0 : 9;
    uint16_t seconds1 : 9;
    uint16_t seconds2 : 9;
    uint8_t pin : 5;
    uint8_t not_pin : 5;
    uint8_t state : 1;
    uint8_t enabled : 1;
    uint8_t enabled0 : 1;
    uint8_t enabled1 : 1;
    uint8_t enabled2 : 1;
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
        digitalWrite(not_pin, HIGH);
    }
} control;

/* Коды модулей */
enum
{
    KEY_GSR = 'G',
    KEY_ECG = 'C',
    KEY_EEG = 'E',
};
const char SERKEYS[3] = {KEY_GSR, KEY_ECG, KEY_EEG};

module GSR;
module ECG;
module EEG;

uint8_t intr_counter;

/* Вывод на экран */
void plotter(uint16_t y)
{
    static uint16_t y0 = 0;
    uint8_t i, mapped;

    // Переворот
    y = 1023 - y;

    // Сдвиг
    for(i = 0; i < 127; i++)
    {
        memcpy(
            &oled._oled_buffer[i * 4],
            &oled._oled_buffer[(i + 1) * 4],
            sizeof(uint8_t) * 4
        );
    }
    // Очистка
    memset(&oled._oled_buffer[127 * 4], 0, sizeof(uint8_t) * 4);
    y = 16.0 * y / analogRead(P0); // верхний потенциометр - аттенюатор
    mapped = (analogRead(P1) - 512) / 8; // нижний потенциометр - смещение
    // Линия
    oled.line(
        126, y0 + mapped,
        127, y + mapped
    );
    y0 = y;
    oled.update();
}

/* Проверка байта на валидность */
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

/* Формирование валидного байта */
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

/* Формовка и запись байта */
uint8_t eeprom_byte_write(uint8_t i)
{
    uint8_t eepromData;
    uint16_t default_time;
    if(i < 6)
    {
        switch(i / 2)
        {
            case 0: default_time = GSR_TIME; break;
            case 1: default_time = ECG_TIME; break;
            case 2: default_time = EEG_TIME; break;
        }
        if(i % 2 == 0)
        {
            eepromData = eeprom_byte_form(default_time & 0b11111, 5);
        }
        else
        {
            eepromData = eeprom_byte_form(((default_time >> 5) & 0b1111) + (1 << 4), 5);
        }
    }
    EEPROM.write(i, eepromData);
    return eepromData;
}

extern volatile unsigned long timer0_millis;

void setup()
{
    uint8_t eepromData, i;
    
    // Базовые I/O
    pinMode(BTN0, INPUT_PULLUP);
    pinMode(LEDR, OUTPUT);
    pinMode(LEDY, OUTPUT);
    pinMode(LEDW, OUTPUT);
    pinMode(13, OUTPUT);
    // Модуль контроля
    control.pin = A3;
    control.not_pin = 12;
    control.setup();
    control.disable();
    control.seconds0 = control.seconds1 = 0;
    // Датчики
    GSR.pin = A2;
    GSR.setup();
    ECG.pin = A1;
    ECG.setup();
    EEG.pin = A0;
    EEG.setup();
    // Чтение и коррекция EEPROM
    for(i = 0; i < 6; i++)
    {
        eepromData = EEPROM.read(i);
        if(eeprom_byte_check(eepromData, 5))
        {
            eeprom_byte_write(i);
        }
        // Распаковка
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
            case 4: {
                control.seconds2 &= 0b111100000;
                control.seconds2 |= eepromData & 0b11111;
            } break;
            case 1: {
                control.seconds0 &= 0b000011111;
                control.seconds0 |= (eepromData & 0b1111) << 5;
                control.enabled0 = (eepromData & 0b10000) >> 4;
            } break;
            case 3: {
                control.seconds1 &= 0b000011111;
                control.seconds1 |= (eepromData & 0b1111) << 5;
                control.enabled1 = (eepromData & 0b10000) >> 4;
            } break;
            case 5: {
                control.seconds2 &= 0b000011111;
                control.seconds2 |= (eepromData & 0b1111) << 5;
                control.enabled2 = (eepromData & 0b10000) >> 4;
            } break;
        }
    }
    // Дисплей
    oled.init();
    Wire.setClock(800000L);
    oled.clear();
    // Отправка данных
    serial.begin(38400);
    // Инициализация глобального таймера
    noInterrupts();
    timer0_millis = GSR_T + E_T + 5000;
    interrupts();
}

void loop()
{
    char S[30], *s[5];
    static uint32_t timer0 = 0, timer1 = 0, timer2 = 0, timer3 = 0, timer4 = 0;
    static uint16_t gsr = 0, ecg = 0, eeg = 0;
    uint16_t t0, t1, t2;
    const uint16_t *val[3] = {&gsr, &ecg, &eeg};
    uint8_t i, btn, e, e0, e1, e2;
    static uint8_t prevBtn = 0, spam_f = 0;

    // Нагрузка
    // if(millis() - timer0 > 100)
    // {
    //     timer0 = millis();
    //     delay(50);
    // } delay(5);

    // Обновление экрана 10 FPS
    if(millis() - timer0 > 100)
    {
        timer0 = millis();
        oled.update();
    }

    // Переключение групп
    if(millis() - timer1 > (control.state ? GSR_T : E_T))
    {
        timer1 = millis();
        control.toggle();
    }

    // Включение/выключение
    control.enabled = !(millis() - timer2 > (GSR_T + E_T));
    if(!control.enabled)
    {
        if(GSR.enabled || ECG.enabled || EEG.enabled)
            spam_f = 10;
        GSR.enabled =
        ECG.enabled =
        EEG.enabled = 0;
        control.state = 0;
        control.disable();
    }
    else
    {
        GSR.enabled = millis() - timer2 > E_T;
        ECG.enabled = millis() - timer2 < ECG_T;
        EEG.enabled = millis() - timer2 < EEG_T;
    }
    digitalWrite(LEDW, GSR.enabled);
    digitalWrite(LEDR, ECG.enabled);
    digitalWrite(LEDY, EEG.enabled);

    // Отправляем код готовности по нажатию кнопки
    btn = digitalRead(BTN0);
    if(btn && !prevBtn && !control.enabled)
        serial.print('s');
    prevBtn = btn;

    // Спамим код завершения
    if(spam_f)
    {
        spam_f -= 1;
        serial.print('f');
    }

    if(serial.available())
        // Формат: e15,10,5,(0b111);
        if(serial.read() == 'e')
        {
            memset(S, 0, sizeof(char) * 30);
            serial.readBytesUntil(';', S, 30);
            sscanf(S, "%d,%d,%d,%d", &t0, &t1, &t2, &e);
            e0 = bitRead(e, 0);
            e1 = bitRead(e, 1);
            e2 = bitRead(e, 2);
            serial.print('D');
            serial.print(control.enabled0);
            serial.print(control.enabled1);
            serial.print(control.enabled2);
            serial.print(',');
            if(t2 != control.seconds0)
            {
                eeprom_byte_write(0);
                eeprom_byte_write(1);
                control.enabled0 = e0;
                control.seconds0 = t2;
            }
            else if(e0 != control.enabled0)
            {
                eeprom_byte_write(1);
                control.enabled0 = e0;
            }
            if(t0 != control.seconds1)
            {
                eeprom_byte_write(2);
                eeprom_byte_write(3);
                control.enabled1 = e1;
                control.seconds1 = t0;
            }
            else if(e1 != control.enabled1)
            {
                eeprom_byte_write(3);
                control.enabled1 = e1;
            }
            if(t1 != control.seconds2)
            {
                eeprom_byte_write(4);
                eeprom_byte_write(5);
                control.enabled2 = e2;
                control.seconds2 = t1;
            }
            else if(e2 != control.enabled2)
            {
                eeprom_byte_write(5);
                control.enabled2 = e2;
            }
            serial.print(control.enabled0);
            serial.print(control.enabled1);
            serial.print(control.enabled2);
            serial.print(';');
            timer1 = timer2 = millis();
        }

    // Считывание
    digitalWrite(DEBUG_LED, HIGH);
    gsr = GSR.read();
    ecg = ECG.read();
    eeg = EEG.read();
    digitalWrite(DEBUG_LED, LOW);

    // Отправка значений в Serial
    if(millis() - timer3 > 3)
    {
        uint8_t mod[3] = {GSR.enabled, ECG.enabled, EEG.enabled};
        timer3 = millis();
        for(i = 0; i < 3; i++)
            if(mod[i] != 0)
            {
                serial.print(SERKEYS[i]);
                serial.print(*val[i]);
                serial.print(';');
            }
    }

    // Вывод значений на экран
    if((millis() - timer4 > 25) && !control.state)
    {
        timer4 = millis();
        plotter(ecg);
    }
}
