# Executor firmware notes

The executor is untested on physical hardware. Firmware compilation and host
logic tests are separate checks; neither verifies servo direction, travel, force,
electrical noise, or behavior after the controller loses power.

## Current behavior

- Seven values are required in each `cmd.q`. Values must be finite numbers;
  booleans, strings, missing joints and malformed JSON are rejected. Finite
  values outside 0..1 are clamped. Validation is atomic: a bad final joint does
  not change earlier joints or refresh the watchdog.
- The 20 ms tick limits each commanded joint change to 0.04. This limits the
  PWM target estimate, not measured physical speed. A first enable or re-enable
  after manually moving a relaxed servo can still move abruptly.
- After 500 ms without a valid command, fingers and opposition ease toward 0;
  the wrist eases toward 0.5. These are provisional rest targets. They become
  a useful open/neutral pose only after calibration on the actual mechanism.
- Startup and `relax` explicitly set the PCA9685 full-off bit on every channel.
  A new valid `cmd` enables motion. `relax` does not cut servo power and is not
  a physical emergency stop.
- `cal` works only while relaxed. Both endpoints must be distinct finite
  numbers in 0..180. Reversed endpoints support a mirrored servo installation.
  Settings are in RAM and reset after reboot. The slider UI starts disabled and
  requires explicit re-enable after calibration or relax.
- Startup angle endpoints are **60 and 120 degrees**. Pulse mapping uses a
  provisional **1000–2000 microsecond** envelope for 0..180 degrees. Consequently
  the default active range is approximately 1333–1667 microseconds, not full
  servo travel. Degree labels are nominal mappings until measured. Measure
  rotation and pulses with tendons disconnected before widening limits.
- Each loop processes at most 128 received bytes. A line longer than 511 bytes
  is discarded through the next newline, so a truncated prefix cannot execute.
  JSON nesting is limited. This prevents continuous serial input from trapping
  the executor in an unbounded input-drain loop.
- Telemetry at 10 Hz reports `q`, `ms`, `relaxed`, `watchdog`, `q_kind` and a
  cumulative `rejected` line count. `q_kind` is `command_estimate`; there are
  no servo encoders. A malformed command is rejected without an acknowledgement.

## Validation

Run all Python/host tests from the repository root:

```powershell
python -m unittest discover -s tests -v
```

`test_firmware_core.py` compiles the actual `executor_state.h` implementation to
WebAssembly using Clang and runs it in Node.js. It checks atomic command rejection,
clamping, rate limiting, watchdog timing including millis wrap, reversed endpoint
calibration, active calibration rejection and relaxed state behavior. It skips if
Clang or Node.js is unavailable. It does not exercise ArduinoJson, I2C or PWM.

Compile for the board without flashing:

```powershell
arduino-cli compile --fqbn esp32:esp32:esp32s3 --build-path build/firmware firmware/hand_executor
```

Required libraries: Adafruit PWM Servo Driver Library, its Adafruit BusIO
dependency, and ArduinoJson 7. Board compilation subsequently passed using
ESP32 core 3.3.12, Adafruit PWM Servo Driver 3.0.3, Adafruit BusIO 1.17.4 and
ArduinoJson 7.4.3. The sketch uses 315,585 bytes of flash and 24,088 bytes of
global RAM with the default `esp32:esp32:esp32s3` build options. Board-specific
flash/PSRAM/USB settings still need confirmation before uploading. No board was
flashed. Compilation and host checks do not establish hardware readiness.

## Bench gate

1. Verify driver logic voltage, separate servo supply and common ground. Start
   with a single unloaded servo and a means to disconnect servo power.
2. Confirm no PWM on startup/relax. Confirm the UI does not restart PWM until
   explicitly enabled. A software relax cannot disable a failed/stalled MCU.
3. While relaxed, set narrow endpoints, then enable. Check direction and pulse
   widths, and widen incrementally without tying a tendon.
4. Attach the single-finger rig only after mechanical range is measured. Confirm
   valid commands stop updating after unplugging serial and the open/rest target
   is reached. Keep logic powered for this test; a power loss is a different case.
5. Send incomplete vectors, strings and an oversized line; confirm the rejected
   counter rises and that the command watchdog still expires.
