// An Arduino sketch for a I2C slave that reads button inputs and sends the
// button number over an I2C bus to a master.
// This is useful for extending the master device by using only the I2C pins
// to read additional pin data from slaves over the bus.

// https://www.arduino.cc/en/Tutorial/MasterWriter
#include <Wire.h>


//

// Pins for connecting buttons to a Arduino Pro Mini-like.
int pins[] = {
  9, 8, 7, 6,
  2, 3, 4, 5,
  15, 14, 13, 12, 11, 10
};

int states[] = {
  0, 0, 0, 0,
  0, 0, 0, 0,
  0, 0, 0, 0, 0, 0
};


//

void setup() {
//  Serial.begin(9600);

  Wire.begin(); // join i2c bus (address optional for master)

  for (int i = 0; i < (sizeof(pins) / sizeof(int)); i++) {
    pinMode(pins[i], INPUT_PULLUP);
  }
}


void loop() {
  int newState;
  for (int i = 0; i < (sizeof(pins) / sizeof(int)); i++) {
    newState = digitalRead(pins[i]);
    if (newState != states[i]) {
      states[i] = newState;
      if (states[i]) {
        Wire.beginTransmission(8); // transmit to device #8
        Wire.write(i);
        Wire.endTransmission();
      } else {
      }
    }
  }

//  delay(5);
}
