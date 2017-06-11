// An Arduino sketch for a fully functioning USB-MIDI device featuring:
// - two octaves worth of black and white keys (starting at MIDI note 53)
// - four rotary encoder knobs (for MIDI Controls 16-19)
// - I2C Master passing integers through MIDI SysEx

// https://www.pjrc.com/teensy/td_midi.html

#define MIDI_CHANNEL 0

// https://www.arduino.cc/en/Tutorial/MasterWriter
#include <Wire.h>

// https://www.pjrc.com/teensy/td_libs_Encoder.html
// This optional setting causes Encoder to use more optimized code,
// It must be defined before Encoder.h is included.
#define ENCODER_OPTIMIZE_INTERRUPTS
#include <Encoder.h>

// Amount of pulses per physical rotary tick.
// Configure this to match your particular rotary encoders.
#define ROTARY_ENCODER_RESOLUTION 4

#define KNOB_1 16
#define KNOB_2 17
#define KNOB_3 18
#define KNOB_4 19

// Teensy 3.2 pins:
// 0-12 D
// 13 LED
// 14-23 A

// note number 60, C4, as "Middle C".
int BASE_NOTE = 53;

// Map of pins to 2 octaves worth of keys.
// For Teensy 3.2.
int pins[] = {
  0, 24, 1, 25, 2, 26, 3,  4, 27, 5, 28, 6,
  7, 29, 8, 30, 9, 31, 10,  11, 32, 12, 33, 13,
};

int states[] = {
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0,  0, 0,  0, 0, 0,  0, 0
};

// 14-17 and 20-23 are all digital pins, which all have interrupts on
// Teensy 3.0 - 3.6.
Encoder knob1(22, 23);
Encoder knob2(20, 21);
Encoder knob3(16, 17);
Encoder knob4(14, 15);

int32_t knobStates[] = {
  0, 0, 0, 0
};


const uint8_t* createSysexArray(uint8_t param, uint8_t value) {
  static uint8_t data[10] = {
    0xF0, 0x41, 0x36, 0x00, 0x23, 0x20, 0x01, 0x0, 0x0, 0xF7
  };
  data[7] = param;
  data[8] = value;
  return data;
}


void readKnob(Encoder* encoder, int32_t* oldState, int control, int channel) {
  int32_t newKnobPosition = encoder->read() / ROTARY_ENCODER_RESOLUTION;

  if (newKnobPosition > 127) {
    newKnobPosition = 127;
    encoder->write(127 * ROTARY_ENCODER_RESOLUTION);
  } else if (newKnobPosition < 0) {
    newKnobPosition = 0;
    encoder->write(0);
  }

  if (newKnobPosition != *oldState) {
    // control, value, channel
    usbMIDI.sendControlChange(control, newKnobPosition, channel);

    (*oldState) = newKnobPosition;
  }
}


void receiveI2CEvent(int numBytes) {
  while (Wire.available()) { // loop through all but the last
    uint8_t button = Wire.read(); // receive byte as a character
//    Serial.print(button); // print button number
    uint8_t data[5] = {
      0xF0, // SysEx start
      0x7D, // manufacturer ID, 0x7D = non-commercial/testing
      button,
      1,
      0xF7 // SysEx end
    };
    usbMIDI.sendSysEx(5, data);
  }
}


void setup() {
//  Serial.begin(9600);

  Wire.begin(8); // join i2c bus with address #8
  Wire.onReceive(receiveI2CEvent); // register event handler

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
        // note, velocity, channel
        usbMIDI.sendNoteOff(BASE_NOTE + i, 100, MIDI_CHANNEL);
      } else {
        usbMIDI.sendNoteOn(BASE_NOTE + i, 100, MIDI_CHANNEL);
      }
    }
  }

  readKnob(&knob1, &(knobStates[0]), KNOB_1, MIDI_CHANNEL);
  readKnob(&knob2, &(knobStates[1]), KNOB_2, MIDI_CHANNEL);
  readKnob(&knob3, &(knobStates[2]), KNOB_3, MIDI_CHANNEL);
  readKnob(&knob4, &(knobStates[3]), KNOB_4, MIDI_CHANNEL);

  delay(5);
}
