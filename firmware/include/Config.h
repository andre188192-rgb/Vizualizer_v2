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
  float vibration_reset;
  float spindle_temp_warn;
  float spindle_temp_alarm;
  float spindle_temp_reset;
};

struct PinConfig {
  uint8_t flow_pin;
  uint8_t ground_pin;
  uint8_t relay_pin;
  uint8_t ds18b20_pin;
  uint8_t acs712_pin;
  uint8_t pzem_rx;
  uint8_t pzem_tx;
  uint8_t mpu_sda;
  uint8_t mpu_scl;
};

struct LoggingConfig {
  uint32_t interval_ms;
  uint8_t sd_warn_percent;
  float spindle_temp_warn;
  float spindle_temp_alarm;
};

struct DeviceConfig {
  WifiConfig wifi;
  Thresholds thresholds;
  PinConfig pins;
  LoggingConfig logging;
  uint32_t snapshot_minutes;
  String mqtt_host;
  uint16_t mqtt_port;
  String mqtt_topic;
};

class ConfigManager {
class ConfigLoader {
 public:
  bool load(DeviceConfig &config) {
    if (!SD.begin()) {
      Serial.println("SD init failed");
      setDefaults(config);
      return false;
    }
    File file = SD.open("/config.json");
    if (!file) {
      Serial.println("config.json not found, creating defaults");
      setDefaults(config);
      save(config);
      return false;
    }
    StaticJsonDocument<1024> doc;
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
      save(config);
      return false;
    }
    config.wifi.ssid = doc["wifi"]["ssid"].as<String>();
    config.wifi.password = doc["wifi"]["password"].as<String>();
    config.thresholds.vibration_warn = doc["thresholds"]["vibration_warn"] | 0.8;
    config.thresholds.vibration_alarm = doc["thresholds"]["vibration_alarm"] | 1.2;
    config.thresholds.vibration_reset = doc["thresholds"]["vibration_reset"] | 0.6;
    config.thresholds.spindle_temp_warn = doc["thresholds"]["spindle_temp_warn"] | 55.0;
    config.thresholds.spindle_temp_alarm = doc["thresholds"]["spindle_temp_alarm"] | 70.0;
    config.thresholds.spindle_temp_reset = doc["thresholds"]["spindle_temp_reset"] | 50.0;
    config.thresholds.spindle_temp_warn = doc["thresholds"]["spindle_temp_warn"] | 55.0;
    config.thresholds.spindle_temp_alarm = doc["thresholds"]["spindle_temp_alarm"] | 70.0;
    config.snapshot_minutes = doc["snapshot_minutes"] | 5;
    config.mqtt_host = doc["mqtt"]["host"].as<String>();
    config.mqtt_port = doc["mqtt"]["port"] | 1883;
    config.mqtt_topic = doc["mqtt"]["topic"] | "cnc/pulse";
    config.logging.interval_ms = doc["logging"]["interval_ms"] | 1000;
    config.logging.sd_warn_percent = doc["logging"]["sd_warn_percent"] | 90;
    config.pins.flow_pin = doc["pins"]["flow_pin"] | 32;
    config.pins.ground_pin = doc["pins"]["ground_pin"] | 33;
    config.pins.relay_pin = doc["pins"]["relay_pin"] | 25;
    config.pins.ds18b20_pin = doc["pins"]["ds18b20_pin"] | 4;
    config.pins.acs712_pin = doc["pins"]["acs712_pin"] | 34;
    config.pins.pzem_rx = doc["pins"]["pzem_rx"] | 16;
    config.pins.pzem_tx = doc["pins"]["pzem_tx"] | 17;
    config.pins.mpu_sda = doc["pins"]["mpu_sda"] | 21;
    config.pins.mpu_scl = doc["pins"]["mpu_scl"] | 22;
    return true;
  }

  bool save(const DeviceConfig &config) {
    if (!SD.begin()) {
      return false;
    }
    StaticJsonDocument<1024> doc;
    doc["wifi"]["ssid"] = config.wifi.ssid;
    doc["wifi"]["password"] = config.wifi.password;
    doc["thresholds"]["vibration_warn"] = config.thresholds.vibration_warn;
    doc["thresholds"]["vibration_alarm"] = config.thresholds.vibration_alarm;
    doc["thresholds"]["vibration_reset"] = config.thresholds.vibration_reset;
    doc["thresholds"]["spindle_temp_warn"] = config.thresholds.spindle_temp_warn;
    doc["thresholds"]["spindle_temp_alarm"] = config.thresholds.spindle_temp_alarm;
    doc["thresholds"]["spindle_temp_reset"] = config.thresholds.spindle_temp_reset;
    doc["snapshot_minutes"] = config.snapshot_minutes;
    doc["mqtt"]["host"] = config.mqtt_host;
    doc["mqtt"]["port"] = config.mqtt_port;
    doc["mqtt"]["topic"] = config.mqtt_topic;
    doc["logging"]["interval_ms"] = config.logging.interval_ms;
    doc["logging"]["sd_warn_percent"] = config.logging.sd_warn_percent;
    doc["pins"]["flow_pin"] = config.pins.flow_pin;
    doc["pins"]["ground_pin"] = config.pins.ground_pin;
    doc["pins"]["relay_pin"] = config.pins.relay_pin;
    doc["pins"]["ds18b20_pin"] = config.pins.ds18b20_pin;
    doc["pins"]["acs712_pin"] = config.pins.acs712_pin;
    doc["pins"]["pzem_rx"] = config.pins.pzem_rx;
    doc["pins"]["pzem_tx"] = config.pins.pzem_tx;
    doc["pins"]["mpu_sda"] = config.pins.mpu_sda;
    doc["pins"]["mpu_scl"] = config.pins.mpu_scl;
    File file = SD.open("/config.json", FILE_WRITE);
    if (!file) {
      return false;
    }
    serializeJson(doc, file);
    file.close();
    return true;
  }

 private:
  void setDefaults(DeviceConfig &config) {
    config.wifi.ssid = "";
    config.wifi.password = "";
    config.thresholds = {0.8f, 1.2f, 0.6f, 55.0f, 70.0f, 50.0f};
    config.thresholds = {0.8f, 1.2f, 55.0f, 70.0f};
    config.snapshot_minutes = 5;
    config.mqtt_host = "";
    config.mqtt_port = 1883;
    config.mqtt_topic = "cnc/pulse";
    config.logging.interval_ms = 1000;
    config.logging.sd_warn_percent = 90;
    config.pins = {32, 33, 25, 4, 34, 16, 17, 21, 22};
  }
};
