// Compile the same control logic used by the ESP32, without board dependencies.
#include "../firmware/hand_executor/executor_state.h"
ExecutorState state;
extern "C" {
void reset() { state = ExecutorState(); }
int command(float value, int count, unsigned long now) {
  float q[7];
  for (int i = 0; i < 7; ++i) q[i] = value;
  return state.command(q, count, now);
}
int badCommand(unsigned long now) {
  float q[7] = {1, 1, 1, 1, 1, 1, __builtin_nanf("")};
  return state.command(q, 7, now);
}
int cal(int joint, float open, float closed) {
  return state.calibrate(joint, open, closed);
}
void tick(unsigned long now) { state.updateWatchdog(now); state.step(); }
void relax() { state.relax(); }
float current(int joint) { return state.current[joint]; }
float target(int joint) { return state.target[joint]; }
float angle(int joint) { return state.angle(joint); }
int relaxed() { return state.relaxed; }
int watchdog() { return state.watchdog; }
unsigned long lastCommand() { return state.lastCommand; }
}
