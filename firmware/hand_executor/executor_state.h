#pragma once

// Platform-independent control logic; also compiled to WebAssembly by host tests.
// q represents the PWM command estimate. These servos have no position feedback.
struct ExecutorState {
  static const int N = 7;
  static constexpr float MAX_STEP = 0.04f;
  static const unsigned long TIMEOUT_MS = 500;
  float openDeg[N], closedDeg[N], target[N], current[N];
  unsigned long lastCommand = 0;
  bool relaxed = true;
  bool watchdog = false;

  ExecutorState() {
    for (int i = 0; i < N; ++i) {
      openDeg[i] = 60;
      closedDeg[i] = 120;
      target[i] = current[i] = rest(i);
    }
  }

  static float rest(int i) { return i == 6 ? 0.5f : 0.0f; }
  static bool finite(float v) { return __builtin_isfinite(v); }
  static float clamp(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
  }

  bool command(const float* q, int count, unsigned long now) {
    if (count != N) return false;
    for (int i = 0; i < N; ++i) if (!finite(q[i])) return false;
    for (int i = 0; i < N; ++i) target[i] = clamp(q[i], 0, 1);
    lastCommand = now;
    relaxed = false;
    watchdog = false;
    return true;
  }

  bool calibrate(int j, float open, float closed) {
    if (!relaxed || j < 0 || j >= N || !finite(open) || !finite(closed) ||
        open < 0 || open > 180 || closed < 0 || closed > 180 || open == closed)
      return false;
    // Reversed endpoints are valid for a mirrored servo installation.
    openDeg[j] = open;
    closedDeg[j] = closed;
    return true;
  }

  void relax() { relaxed = true; watchdog = false; }

  void updateWatchdog(unsigned long now) {
    // ESP32 unsigned long wraps at 32 bits; subtraction remains valid over wrap.
    if (!relaxed && now - lastCommand >= TIMEOUT_MS) {
      watchdog = true;
      for (int i = 0; i < N; ++i) target[i] = rest(i);
    }
  }

  void step() {
    if (relaxed) return;
    for (int i = 0; i < N; ++i)
      current[i] += clamp(target[i] - current[i], -MAX_STEP, MAX_STEP);
  }

  float angle(int i) const {
    return openDeg[i] + current[i] * (closedDeg[i] - openDeg[i]);
  }
};
