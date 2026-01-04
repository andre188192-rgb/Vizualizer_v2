#pragma once

#include <Arduino.h>
#include <SD.h>
#include "Config.h"
#include "SensorReadings.h"

class DataLogger {
 public:
  bool begin() { return SD.begin(); }

  void configure(const LoggingConfig &config) { warn_percent = config.sd_warn_percent; }

  bool ensureReady() {
    if (!SD.begin()) {
      Serial.println("SD unavailable");
      return false;
    }
    if (!SD.exists("/logs")) {
      SD.mkdir("/logs");
    }
    return true;
  }

  void logReadings(const SensorReadings &readings) {
    if (!ensureReady()) {
      return;
    }
    checkStorage();
    rotateIfNeeded();
    File file = SD.open(currentLogFile().c_str(), FILE_APPEND);
    if (!file) {
      Serial.println("Failed to open log file");
      return;
    }
    file.printf(
        "%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%.3f,%.2f,%d,%lu\n",
        readings.timestamp.c_str(),
        readings.voltage,
        readings.current,
        readings.power,
        readings.flow_rate,
        readings.spindle_temp,
        readings.vibration_rms,
        readings.vibration_x_rms,
        readings.vibration_y_rms,
        readings.vibration_z_rms,
        readings.motor_current,
        readings.ground_present ? 1 : 0,
        readings.cycle_count);
    file.close();
  }

 private:
  const size_t max_log_size = 5 * 1024 * 1024;
  const uint8_t max_log_files = 5;
  uint8_t warn_percent = 90;

  String currentLogFile() { return "/logs/cnc_log.csv"; }

  void rotateIfNeeded() {
    File file = SD.open(currentLogFile().c_str(), FILE_READ);
    if (!file) {
      return;
    }
    size_t size = file.size();
    file.close();
    if (size < max_log_size) {
      return;
    }
    Serial.println("SD_LOG_ROTATE");
    String rotated = "/logs/cnc_log_" + String(millis()) + ".csv";
    SD.rename(currentLogFile().c_str(), rotated.c_str());
    cleanupOldLogs();
  }

  void checkStorage() {
    uint64_t total = SD.totalBytes();
    uint64_t used = SD.usedBytes();
    if (total == 0) {
      return;
    }
    uint8_t percent = static_cast<uint8_t>((used * 100) / total);
    if (percent >= warn_percent) {
      Serial.println("SD_NEAR_FULL");
    }
  }

  void cleanupOldLogs() {
    File root = SD.open("/logs");
    if (!root) {
      return;
    }
    uint8_t count = 0;
    File file = root.openNextFile();
    while (file) {
      if (!file.isDirectory()) {
        count++;
      }
      file = root.openNextFile();
    }
    root.close();
    if (count <= max_log_files) {
      return;
    }
    File rootDelete = SD.open("/logs");
    File oldest = rootDelete.openNextFile();
    while (oldest && count > max_log_files) {
      if (!oldest.isDirectory()) {
        String name = oldest.name();
        oldest.close();
        SD.remove(name.c_str());
        count--;
      } else {
        oldest.close();
      }
      oldest = rootDelete.openNextFile();
    }
    rootDelete.close();
  }
};
