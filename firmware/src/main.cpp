#include <Arduino.h>
#include <SD.h>
#include <esp_task_wdt.h>
#include <time.h>
#include "Config.h"
#include "SensorReadings.h"
#include "Sensors.h"
#include "DataLogger.h"
#include "NetworkManager.h"

static DeviceConfig deviceConfig;
static SensorManager sensorManager;
static DataLogger dataLogger;
static NetworkManager networkManager;
static SensorReadings latestReadings;
static uint32_t cycleCount = 0;
static bool relayAlarm = false;

TaskHandle_t sensorTaskHandle;
TaskHandle_t loggerTaskHandle;
TaskHandle_t networkTaskHandle;

String timestampNow() {
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    char buffer[24];
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &timeinfo);
    return String(buffer);
  }
  return String(millis());
}

String classifyState(const SensorReadings &readings) {
  if (readings.vibration_rms >= deviceConfig.thresholds.vibration_alarm ||
      readings.spindle_temp >= deviceConfig.thresholds.spindle_temp_alarm) {
    return "ALARM";
  }
  if (readings.vibration_rms >= deviceConfig.thresholds.vibration_warn ||
      readings.spindle_temp >= deviceConfig.thresholds.spindle_temp_warn) {
    return "WARN";
  }
  return "NORMAL";
}

void updateRelay(const SensorReadings &readings) {
  if (relayAlarm) {
    if (readings.vibration_rms < deviceConfig.thresholds.vibration_reset &&
        readings.spindle_temp < deviceConfig.thresholds.spindle_temp_reset) {
      relayAlarm = false;
    }
  } else {
    if (readings.vibration_rms >= deviceConfig.thresholds.vibration_alarm ||
        readings.spindle_temp >= deviceConfig.thresholds.spindle_temp_alarm) {
      relayAlarm = true;
    }
  }
  sensorManager.setAlarmRelay(relayAlarm);
}

void sensorTask(void *param) {
  for (;;) {
    sensorManager.sample(latestReadings);
    latestReadings.timestamp = timestampNow();
    latestReadings.cycle_count = cycleCount;
    esp_task_wdt_reset();
    vTaskDelay(pdMS_TO_TICKS(200));
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

void loggerTask(void *param) {
  for (;;) {
    dataLogger.logReadings(latestReadings);
    esp_task_wdt_reset();
    vTaskDelay(pdMS_TO_TICKS(deviceConfig.logging.interval_ms));
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void networkTask(void *param) {
  for (;;) {
    networkManager.loop();
    String state = classifyState(latestReadings);
    updateRelay(latestReadings);
    networkManager.publishMetrics(latestReadings, state);
    esp_task_wdt_reset();
    networkManager.publishMetrics(latestReadings, state);
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  ConfigManager loader;
  loader.load(deviceConfig);

  sensorManager.begin(deviceConfig);
  dataLogger.begin();
  dataLogger.configure(deviceConfig.logging);
  ConfigLoader loader;
  loader.load(deviceConfig);

  sensorManager.begin();
  dataLogger.begin();
  networkManager.begin(deviceConfig);

  configTime(0, 0, "pool.ntp.org", "time.nist.gov");

  esp_task_wdt_init(10, true);
  esp_task_wdt_add(nullptr);
  if (!SD.exists("/logs")) {
    SD.mkdir("/logs");
  }

  xTaskCreatePinnedToCore(sensorTask, "SensorTask", 4096, nullptr, 2, &sensorTaskHandle, 1);
  xTaskCreatePinnedToCore(loggerTask, "LoggerTask", 4096, nullptr, 1, &loggerTaskHandle, 1);
  xTaskCreatePinnedToCore(networkTask, "NetworkTask", 4096, nullptr, 1, &networkTaskHandle, 0);
}

void loop() {
  static bool lastPower = false;
  bool powerPresent = latestReadings.voltage > 10.0f;
  if (powerPresent && !lastPower) {
    cycleCount++;
  }
  lastPower = powerPresent;
  esp_task_wdt_reset();
  delay(1000);
}
