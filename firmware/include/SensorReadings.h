#pragma once

#include <Arduino.h>

static constexpr float SENSOR_ERROR_VALUE = -999.0f;

enum class SensorStatus {
  OK,
  ERROR,
  TIMEOUT
};

struct SensorReadings {
  float voltage = SENSOR_ERROR_VALUE;
  float current = SENSOR_ERROR_VALUE;
  float power = SENSOR_ERROR_VALUE;
  float flow_rate = SENSOR_ERROR_VALUE;
  float spindle_temp = SENSOR_ERROR_VALUE;
  float vibration_rms = SENSOR_ERROR_VALUE;
  float vibration_x_rms = SENSOR_ERROR_VALUE;
  float vibration_y_rms = SENSOR_ERROR_VALUE;
  float vibration_z_rms = SENSOR_ERROR_VALUE;
  float motor_current = SENSOR_ERROR_VALUE;
  bool ground_present = false;
  uint32_t cycle_count = 0;
  String timestamp;
  SensorStatus pzem_status = SensorStatus::ERROR;
  SensorStatus mpu_status = SensorStatus::ERROR;
  SensorStatus temp_status = SensorStatus::ERROR;
  SensorStatus flow_status = SensorStatus::ERROR;
  SensorStatus current_status = SensorStatus::ERROR;
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
