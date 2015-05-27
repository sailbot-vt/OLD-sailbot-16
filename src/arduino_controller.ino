#define uint  unsigned int
#define ulong unsigned long
#include <Servo.h>
#include <EEPROM.h>
#include <Wire.h>

#include <math.h>

#define PIN_SWITCH      2     // Digital 2
#define PIN_SERVO       3     // Digital 3
#define PIN_WINCH       4     // Digital 4

int switchSignal;
int servoSignal;
int winchSignal;

//=======================================================
// Initialize
//=======================================================
void setup() {
    Serial.begin(9600);
    Wire.begin(2); // Join i2c bus with address #2
    Wire.onRequest(requestEvent); // Register event
    Wire.onReceive(receiveEvent); // Register event
}

//=======================================================
// Main loop.
//=======================================================
void loop() {

    // 20 reads per second
    delay(50);

    switchSignal = readPulse(PIN_SWITCH);
    servoSignal = readPulse(PIN_SERVO);
    winchSignal = readPulse(PIN_WINCH);
}

int readPulse(int pin) {
    return pulseIn(pin, HIGH);
}

// Data to send to I2C Master
void requestEvent() {
    static uint8_t buff[1];
    buff[0] = switchSignal;
    buff[1] = servoSignal;
    buff[2] = winchSignal;
    Wire.write(buff, 3); // Respond with message of 6 bytes as expected by master

    /*
    Serial.println(switchSignal);
    Serial.println(servoSignal);
    Serial.println(winchSignal);
    */
}

// Data to receive from I2C Master
void receiveEvent(int howMany) {
    int b;
    while (Wire.available() > 0) {
        b = Wire.read();
        Serial.println(b);
    }
}