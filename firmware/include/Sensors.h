#pragma once

#include <Arduino.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include "SensorReadings.h"

class SensorManager {
 public:
  void begin() {
    pinMode(flow_pin, INPUT_PULLUP);
    pinMode(ground_pin, INPUT_PULLUP);
    pinMode(relay_pin, OUTPUT);
    digitalWrite(relay_pin, LOW);
    oneWire.begin(ds18b20_pin);
    tempSensor.begin();
  }

  void sample(SensorReadings &readings) {
    readings.voltage = 220.0f + random(-2, 3) * 0.5f;
    readings.current = 8.5f + random(-3, 3) * 0.2f;
    readings.power = readings.voltage * readings.current;
    readings.flow_rate = 2.5f + random(-2, 2) * 0.1f;

    tempSensor.requestTemperatures();
    float temp = tempSensor.getTempCByIndex(0);
    readings.spindle_temp = temp > -100 ? temp : readings.spindle_temp;

    readings.vibration_rms = 0.6f + random(-3, 3) * 0.05f;
    readings.driver_current = 3.2f + random(-2, 2) * 0.1f;
    readings.ground_present = digitalRead(ground_pin) == HIGH;
  }

  void setAlarmRelay(bool enabled) { digitalWrite(relay_pin, enabled ? HIGH : LOW); }

 private:
  const uint8_t flow_pin = 32;
  const uint8_t ground_pin = 33;
  const uint8_t relay_pin = 25;
  const uint8_t ds18b20_pin = 4;
  OneWire oneWire{ds18b20_pin};
  DallasTemperature tempSensor{&oneWire};
};
