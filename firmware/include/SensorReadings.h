#pragma once

#include <Arduino.h>

struct SensorReadings {
  float voltage;
  float current;
  float power;
  float flow_rate;
  float spindle_temp;
  float vibration_rms;
  float driver_current;
  bool ground_present;
  uint32_t cycle_count;
  String timestamp;
};
