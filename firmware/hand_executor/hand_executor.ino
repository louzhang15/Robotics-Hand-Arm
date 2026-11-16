// ESP32-S3 + PCA9685; one JSON object per line at 115200 baud.
// Channels: thumb flex, thumb opposition, index, middle, ring, pinky, wrist.
// GPIO 8 -> SDA, GPIO 9 -> SCL; 3V3 -> VCC; separate servo power, common GND.
// Unmeasured defaults are for unloaded commissioning, NOT verified end stops.
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>
#include "executor_state.h"

Adafruit_PWMServoDriver pca(0x40);
ExecutorState state;
const unsigned long TICK_MS = 20;
// Conservative provisional pulse envelope. Measure the real servo before widening.
const unsigned int US_MIN = 1000, US_MAX = 2000;
unsigned long lastTick = 0, lastTelemetry = 0;
unsigned long rejected = 0;

void disableOutputs() {
  // PCA9685 full-off flag; (0,0) is not an explicit full-off command.
  for (int i = 0; i < 16; ++i) pca.setPWM(i, 0, 4096);
}

bool number(JsonVariantConst value) {
  return !value.is<bool>() && value.is<float>();
}

bool handleLine(const char* line, size_t length) {
  JsonDocument doc;
  if (deserializeJson(doc, line, length, DeserializationOption::NestingLimit(4)))
    return false;
  if (!doc.is<JsonObject>() || !doc["t"].is<const char*>()) return false;
  const char* type = doc["t"].as<const char*>();
  if (!strcmp(type, "cmd")) {
    if (!doc["q"].is<JsonArray>() || doc["q"].size() != ExecutorState::N)
      return false;
    float values[ExecutorState::N];
    for (int i = 0; i < ExecutorState::N; ++i) {
      if (!number(doc["q"][i])) return false;
      values[i] = doc["q"][i].as<float>();
    }
    return state.command(values, ExecutorState::N, millis());
  }
  if (!strcmp(type, "cal")) {
    if (doc["j"].is<bool>() || !doc["j"].is<int>() ||
        !number(doc["min"]) || !number(doc["max"])) return false;
    return state.calibrate(doc["j"].as<int>(), doc["min"].as<float>(),
                           doc["max"].as<float>());
  }
  if (!strcmp(type, "relax")) {
    state.relax();
    disableOutputs();
    return true;
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 9);
  if (!pca.begin()) {
    // No driver: do not proceed into an executor that appears healthy.
    while (true) delay(1000);
  }
  disableOutputs();
  pca.setOscillatorFrequency(25000000); // library nominal; measure before tuning
  pca.setPWMFreq(50);
  disableOutputs();
}

void loop() {
  static char buffer[512];
  static size_t length = 0;
  static bool dropping = false;
  // A continuous malformed stream must not starve the watchdog or motion tick.
  for (int budget = 0; budget < 128 && Serial.available(); ++budget) {
    char c = Serial.read();
    if (c == '\n') {
      if (!dropping && length && !handleLine(buffer, length)) ++rejected;
      if (dropping) ++rejected;
      length = 0;
      dropping = false;
    } else if (!dropping) {
      if (length < sizeof(buffer) - 1) buffer[length++] = c;
      else { dropping = true; length = 0; }
    }
  }

  unsigned long now = millis();
  state.updateWatchdog(now);
  if (now - lastTick >= TICK_MS) {
    lastTick = now;
    state.step();
    if (!state.relaxed) {
      for (int i = 0; i < ExecutorState::N; ++i) {
        float us = US_MIN + state.angle(i) / 180.0f * (US_MAX - US_MIN);
        pca.writeMicroseconds(i, static_cast<unsigned int>(us));
      }
    }
  }

  if (now - lastTelemetry >= 100) {
    lastTelemetry = now;
    JsonDocument tel;
    tel["t"] = "tel";
    JsonArray q = tel["q"].to<JsonArray>();
    for (int i = 0; i < ExecutorState::N; ++i) q.add(state.current[i]);
    tel["ms"] = now;
    tel["relaxed"] = state.relaxed;
    tel["watchdog"] = state.watchdog;
    tel["q_kind"] = "command_estimate";
    tel["rejected"] = rejected;
    serializeJson(tel, Serial);
    Serial.println();
  }
}
