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
    WiFi.mode(WIFI_STA);
    WiFi.begin(settings.wifi.ssid.c_str(), settings.wifi.password.c_str());
    client.setServer(settings.mqtt_host.c_str(), settings.mqtt_port);
  }

  void loop() {
    if (WiFi.status() != WL_CONNECTED) {
      reconnectWifi();
      return;
    }
    if (!client.connected()) {
      reconnectMqtt();
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
  uint32_t lastWifiAttempt = 0;
  uint32_t lastMqttAttempt = 0;

  void reconnectWifi() {
    if (millis() - lastWifiAttempt < 5000) {
      return;
    }
    lastWifiAttempt = millis();
    WiFi.disconnect();
    WiFi.begin(settings.wifi.ssid.c_str(), settings.wifi.password.c_str());
  }

  void reconnectMqtt() {
    if (settings.mqtt_host.length() == 0) {
      return;
    }
    if (millis() - lastMqttAttempt < 5000) {
      return;
    }
    lastMqttAttempt = millis();
    String clientId = "cnc-pulse-" + String(random(0xffff), HEX);
    client.connect(clientId.c_str());
  }
};
