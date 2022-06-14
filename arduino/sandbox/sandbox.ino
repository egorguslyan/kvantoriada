#define ARR_SIZE 256
#define GSR_TIME 300
#define ECG_TIME 1000

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
    uint8_t state : 1;
    void updpins()
    {
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
        state = !state;
        updpins();
    }
} control;

module GSR;

void setup()
{
    pinMode(13, OUTPUT);
    control.pin = A3;
    control.not_pin = 12;
    control.state = 1;
    control.setup();
    GSR.pin = A2;
    GSR.setup();
    noInterrupts(); {
        TCCR1A = 0;
        TCCR1B = 0;
        TIMSK1 = (1 << TOIE1);
        TCCR1B |= (1 << CS10);
        //TCCR1B |= (1 << CS11);
    } interrupts();
    Serial.begin(9600);
    delay(10);
}

void loop()
{
    char S[10];
    static uint32_t timer0, timer1;
    volatile uint8_t gsr[ARR_SIZE];
    uint8_t i;

    if(millis() - timer0 > 100)
    {
        timer0 = millis();
        delay(50);
    } delay(5);

    if(millis() - timer1 > (control.state ? GSR_TIME : ECG_TIME))
    {
        timer1 = millis();
        control.toggle();
    }

    // if(control.state)
        GSR.pop(gsr);
    shiftOut(11, 11, 0, gsr[0]);    // volatile didn't help
    for(i = 1; i <= gsr[0]; i++)
    {
        sprintf(S, "%d %d", 0, control.state ? gsr[i] : 0);
        Serial.println(S);
    }
    gsr[0] = 0;
}

ISR(TIMER1_OVF_vect)
{
    digitalWrite(13, HIGH);
    GSR.enabled = control.state;
    GSR.read();
    digitalWrite(13, LOW);
}