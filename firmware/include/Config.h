#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <SD.h>

struct WifiConfig {
  String ssid;
  String password;
};

struct Thresholds {
  float vibration_warn;
  float vibration_alarm;
  float spindle_temp_warn;
  float spindle_temp_alarm;
};

struct DeviceConfig {
  WifiConfig wifi;
  Thresholds thresholds;
  uint32_t snapshot_minutes;
  String mqtt_host;
  uint16_t mqtt_port;
  String mqtt_topic;
};

class ConfigLoader {
 public:
  bool load(DeviceConfig &config) {
    if (!SD.begin()) {
      Serial.println("SD init failed");
      return false;
    }
    File file = SD.open("/config.json");
    if (!file) {
      Serial.println("config.json not found, using defaults");
      setDefaults(config);
      return false;
    }
    StaticJsonDocument<768> doc;
    DeserializationError err = deserializeJson(doc, file);
    file.close();
    if (err) {
      Serial.println("Failed to parse config.json, using defaults");
      setDefaults(config);
      return false;
    }
    config.wifi.ssid = doc["wifi"]["ssid"].as<String>();
    config.wifi.password = doc["wifi"]["password"].as<String>();
    config.thresholds.vibration_warn = doc["thresholds"]["vibration_warn"] | 0.8;
    config.thresholds.vibration_alarm = doc["thresholds"]["vibration_alarm"] | 1.2;
    config.thresholds.spindle_temp_warn = doc["thresholds"]["spindle_temp_warn"] | 55.0;
    config.thresholds.spindle_temp_alarm = doc["thresholds"]["spindle_temp_alarm"] | 70.0;
    config.snapshot_minutes = doc["snapshot_minutes"] | 5;
    config.mqtt_host = doc["mqtt"]["host"].as<String>();
    config.mqtt_port = doc["mqtt"]["port"] | 1883;
    config.mqtt_topic = doc["mqtt"]["topic"] | "cnc/pulse";
    return true;
  }

 private:
  void setDefaults(DeviceConfig &config) {
    config.wifi.ssid = "";
    config.wifi.password = "";
    config.thresholds = {0.8f, 1.2f, 55.0f, 70.0f};
    config.snapshot_minutes = 5;
    config.mqtt_host = "";
    config.mqtt_port = 1883;
    config.mqtt_topic = "cnc/pulse";
  }
};
