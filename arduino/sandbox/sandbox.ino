#define ARR_SIZE 256
#define GSR_TIME 300
#define ECG_TIME 20000
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
volatile uint8_t start;

void setup()
{
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
    static uint32_t timer0, timer1;
    volatile uint8_t gsr[ARR_SIZE], ecg[ARR_SIZE], eeg[ARR_SIZE];
    uint8_t i, btn, prevBtn;

    if(millis() - timer0 > 100)
    {
        timer0 = millis();
        delay(50);
    } delay(5);

    if(millis() - timer1 > GSR_TIME)
    {
        timer1 = millis();
        control.toggle();
        if(control.state)
        {
            start = 0;
            control.disable();
        }
    }

    btn = digitalRead(BTN);
    if(!prevBtn && btn)
    {
        start = 1;
        timer1 = millis();
        control.set(1);
    }
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
    if((intr_counter >= 10) && start)
    {
        intr_counter = 0;
        digitalWrite(13, HIGH);
        GSR.enabled = control.state && control.enabled;
        ECG.enabled = !control.state && control.enabled;
        EEG.enabled = !control.state && control.enabled;
        GSR.read();
        ECG.read();
        EEG.read();
        digitalWrite(13, LOW);
    }
}