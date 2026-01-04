#pragma once

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "SensorReadings.h"
#include "Config.h"

class NetworkManager {
 public:
  NetworkManager() : client(wifi) {}

  void begin(const DeviceConfig &config) {
    settings = config;
    if (settings.wifi.ssid.length() == 0) {
      Serial.println("WiFi SSID not configured");
      return;
    }
    WiFi.begin(settings.wifi.ssid.c_str(), settings.wifi.password.c_str());
    client.setServer(settings.mqtt_host.c_str(), settings.mqtt_port);
  }

  void loop() {
    if (WiFi.status() != WL_CONNECTED) {
      return;
    }
    if (!client.connected()) {
      reconnect();
    }
    client.loop();
  }

  void publishMetrics(const SensorReadings &readings, const String &state) {
    if (!client.connected()) {
      return;
    }
    StaticJsonDocument<512> doc;
    doc["timestamp"] = readings.timestamp;
    doc["state"] = state;
    doc["voltage"] = readings.voltage;
    doc["current"] = readings.current;
    doc["power"] = readings.power;
    doc["flow_rate"] = readings.flow_rate;
    doc["spindle_temp"] = readings.spindle_temp;
    doc["vibration_rms"] = readings.vibration_rms;
    doc["driver_current"] = readings.driver_current;
    doc["ground_present"] = readings.ground_present;
    doc["cycle_count"] = readings.cycle_count;
    String payload;
    serializeJson(doc, payload);
    client.publish(settings.mqtt_topic.c_str(), payload.c_str());
  }

 private:
  WiFiClient wifi;
  PubSubClient client;
  DeviceConfig settings;

  void reconnect() {
    if (settings.mqtt_host.length() == 0) {
      return;
    }
    String clientId = "cnc-pulse-" + String(random(0xffff), HEX);
    client.connect(clientId.c_str());
  }
};
