#define ARR_SIZE 256

struct module
{
    uint8_t pin : 4;
    uint8_t control : 5;
    uint8_t enabled : 1;
    volatile uint8_t buffer[ARR_SIZE];
    void setup()
    {
        pinMode(pin, INPUT);
        pinMode(control, OUTPUT);
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
} GSR;

void setup()
{
    pinMode(13, OUTPUT);
    GSR.pin = A0;
    GSR.control = A3;
    GSR.setup();
    noInterrupts(); {
        TCCR1A = 0;
        TCCR1B = 0;
        TIMSK1 = (1 << TOIE1);
        TCCR1B |= (1 << CS10);
        //TCCR1B |= (1 << CS11);
    } interrupts();
    digitalWrite(GSR.control, HIGH);
    Serial.begin(9600);
    delay(10);
}

void loop()
{
    static uint32_t timer0;
    volatile uint8_t arr[ARR_SIZE];
    uint8_t i;

    if(millis() - timer0 > 100)
    {
        timer0 = millis();
        delay(50);
    }

    GSR.pop(arr);
    shiftOut(11, 11, 0, arr[0]);
    for(i = 1; i <= arr[0]; i++)
    {
        Serial.println(arr[i]);
    }
}

ISR(TIMER1_OVF_vect)
{
    digitalWrite(13, HIGH);
    GSR.read();
    digitalWrite(13, LOW);
}