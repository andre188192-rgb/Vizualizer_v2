#pragma once

#include <Arduino.h>
#include <SD.h>
#include "SensorReadings.h"

class DataLogger {
 public:
  bool begin() {
    if (!SD.begin()) {
      Serial.println("Failed to init SD for logger");
      return false;
    }
    return true;
  }

  void logReadings(const SensorReadings &readings) {
    File file = SD.open(currentLogFile().c_str(), FILE_APPEND);
    if (!file) {
      Serial.println("Failed to open log file");
      return;
    }
    file.printf("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.3f,%.2f,%d,%lu\n",
                readings.timestamp.c_str(),
                readings.voltage,
                readings.current,
                readings.power,
                readings.flow_rate,
                readings.spindle_temp,
                readings.vibration_rms,
                readings.driver_current,
                readings.ground_present ? 1 : 0,
                readings.cycle_count);
    file.close();
  }

 private:
  String currentLogFile() {
    return "/logs/cnc_log.csv";
  }
};
