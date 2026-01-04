#pragma once

#include <Arduino.h>
#include "SensorReadings.h"

class SensorManager {
 public:
  void begin() {
    pinMode(flow_pin, INPUT_PULLUP);
    pinMode(ground_pin, INPUT_PULLUP);
  }

  void sample(SensorReadings &readings) {
    readings.voltage = 220.0f + random(-2, 3) * 0.5f;
    readings.current = 8.5f + random(-3, 3) * 0.2f;
    readings.power = readings.voltage * readings.current;
    readings.flow_rate = 2.5f + random(-2, 2) * 0.1f;
    readings.spindle_temp = 42.0f + random(-2, 2) * 0.4f;
    readings.vibration_rms = 0.6f + random(-3, 3) * 0.05f;
    readings.driver_current = 3.2f + random(-2, 2) * 0.1f;
    readings.ground_present = digitalRead(ground_pin) == HIGH;
  }

 private:
  const uint8_t flow_pin = 32;
  const uint8_t ground_pin = 33;
};
