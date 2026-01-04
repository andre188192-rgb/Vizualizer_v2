#pragma once

#include <Arduino.h>
#include <PZEM004Tv30.h>
#include <Wire.h>
#include <MPU6050.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include "Config.h"
#include "SensorReadings.h"

class SensorManager {
 public:
  void begin(const DeviceConfig &config) {
    settings = config;
    pinMode(settings.pins.flow_pin, INPUT_PULLUP);
    pinMode(settings.pins.ground_pin, INPUT_PULLUP);
    pinMode(settings.pins.relay_pin, OUTPUT);
    digitalWrite(settings.pins.relay_pin, LOW);

    oneWire = OneWire(settings.pins.ds18b20_pin);
    tempSensor = DallasTemperature(&oneWire);
    tempSensor.begin();

    Wire.begin(settings.pins.mpu_sda, settings.pins.mpu_scl);
    Wire.setWireTimeout(3000, true);
    mpu.initialize();

    Serial2.begin(9600, SERIAL_8N1, settings.pins.pzem_rx, settings.pins.pzem_tx);
    pzem = new PZEM004Tv30(Serial2);
    setupFlowInterrupt();
  }

  void sample(SensorReadings &readings) {
    readPzem(readings);
    readMpu(readings);
    readTemperature(readings);
    readFlow(readings);
    readMotorCurrent(readings);
    readings.ground_present = digitalRead(settings.pins.ground_pin) == HIGH;
  }

  void setAlarmRelay(bool enabled) { digitalWrite(settings.pins.relay_pin, enabled ? HIGH : LOW); }

 private:
  DeviceConfig settings;
  OneWire oneWire{0};
  DallasTemperature tempSensor{&oneWire};
  MPU6050 mpu;
  PZEM004Tv30 *pzem = nullptr;
  volatile uint32_t flow_pulse_count = 0;
  uint32_t last_flow_read_ms = 0;

  void setupFlowInterrupt() {
    attachInterruptArg(
        settings.pins.flow_pin,
        [](void *arg) {
          auto *self = static_cast<SensorManager *>(arg);
          self->flow_pulse_count++;
        },
        this,
        RISING);
  }

  bool isPzemConnected() { return pzem && !isnan(pzem->voltage()); }

  bool isMpuConnected() {
    uint8_t who = mpu.getDeviceID();
    return who == 0x68 || who == 0x69;
  }

  void readPzem(SensorReadings &readings) {
    if (!isPzemConnected()) {
      Serial.println("SENSOR_ERROR: PZEM004T no response");
      readings.pzem_status = SensorStatus::ERROR;
      readings.voltage = SENSOR_ERROR_VALUE;
      readings.current = SENSOR_ERROR_VALUE;
      readings.power = SENSOR_ERROR_VALUE;
      return;
    }
    readings.voltage = pzem->voltage();
    readings.current = pzem->current();
    readings.power = pzem->power();
    readings.pzem_status = SensorStatus::OK;
  }

  void readMpu(SensorReadings &readings) {
    if (!isMpuConnected()) {
      Serial.println("SENSOR_ERROR: MPU6050 no response");
      readings.mpu_status = SensorStatus::ERROR;
      readings.vibration_rms = SENSOR_ERROR_VALUE;
      readings.vibration_x_rms = SENSOR_ERROR_VALUE;
      readings.vibration_y_rms = SENSOR_ERROR_VALUE;
      readings.vibration_z_rms = SENSOR_ERROR_VALUE;
      return;
    }
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    float gx = ax / 16384.0f;
    float gy = ay / 16384.0f;
    float gz = az / 16384.0f;
    readings.vibration_x_rms = fabs(gx);
    readings.vibration_y_rms = fabs(gy);
    readings.vibration_z_rms = fabs(gz);
    readings.vibration_rms = sqrtf((gx * gx + gy * gy + gz * gz) / 3.0f);
    readings.mpu_status = SensorStatus::OK;
  }

  void readTemperature(SensorReadings &readings) {
    tempSensor.requestTemperatures();
    float temp = tempSensor.getTempCByIndex(0);
    if (temp < -100 || temp > 150) {
      Serial.println("SENSOR_ERROR: DS18B20 invalid reading");
      readings.temp_status = SensorStatus::ERROR;
      readings.spindle_temp = SENSOR_ERROR_VALUE;
      return;
    }
    readings.spindle_temp = temp;
    readings.temp_status = SensorStatus::OK;
  }

  void readFlow(SensorReadings &readings) {
    uint32_t now = millis();
    if (last_flow_read_ms == 0) {
      last_flow_read_ms = now;
      readings.flow_rate = 0.0f;
      readings.flow_status = SensorStatus::OK;
      return;
    }
    uint32_t elapsed_ms = now - last_flow_read_ms;
    if (elapsed_ms < 1000) {
      return;
    }
    uint32_t pulses = flow_pulse_count;
    flow_pulse_count = 0;
    last_flow_read_ms = now;
    float freq = pulses / (elapsed_ms / 1000.0f);
    readings.flow_rate = freq / 7.5f;  // YF-S201: 7.5 pulses per L/min
    readings.flow_status = SensorStatus::OK;
  }

  void readMotorCurrent(SensorReadings &readings) {
    int raw = analogRead(settings.pins.acs712_pin);
    float voltage = (raw / 4095.0f) * 3.3f;
    float current = (voltage - 1.65f) / 0.066f;
    readings.motor_current = current;
    readings.current_status = SensorStatus::OK;
  }
};
