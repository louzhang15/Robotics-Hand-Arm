# Build status - 16 November 2026

The digital build pass prepares the project for measured bench commissioning.
No servo has been driven, board flashed, hardware fit confirmed, or print started.
The robot itself is not yet physically validated.

## Completed work

- Converted the pasted PRD to `docs/PRD.md`, preserving all 2,419 source words in order.
- Imported the supplied ZIP without overwriting the converted PRD or original assets.
- Fixed manual-control Relax so subsequent 20 Hz ticks cannot re-enable motion.
  The app starts disabled and calibration requires explicit re-enabling.
- Added exact-length, finite-number command validation, robust telemetry reading,
  clean shutdown, nested logging-folder creation and a hardware-free Hand mode.
- Replaced legacy webcam control with a current MediaPipe Tasks implementation;
  isolated geometry for tests and made the model path explicit.
- Added a measured-first build sequence, worksheet and configurable design calculations.
- Audited original 3MF metadata: **the embedded material is PLA**, not the PETG
  claimed in the supplied document. A1/0.4 mm, 0.2 mm layers, four walls, 30%
  gyroid and supports disabled are embedded; this is not a verified slice.

## Checks

Python command/geometry tests and source syntax checks pass. The original two STL
files each have one connected component, no boundary/nonmanifold edges, no winding
errors and no degenerate triangles in the included topology check. Their bounding
dimensions fit a nominal 256 mm cube. Those results do not establish real fit,
strength, slicer behavior or extrusion clearance.

All **16 automated tests pass**, including a test that compiles the actual C++
executor state implementation to WebAssembly and runs it in Node.js. Firmware
board compilation passed for `esp32:esp32:esp32s3` with ESP32 core 3.3.12:
315,585 bytes flash and 24,088 bytes global RAM. See `firmware-notes.md` for the
library versions and hardware limitations.

OpenSCAD successfully evaluated the new forearm source and generated the chassis,
servo cartridge and service adapter STL files, plus an assembly PNG under
`cad/generated/`. See the CAD README for topology checks and concept limitations.
All three final STL exports have one connected component, no boundary or
nonmanifold edges, no winding errors and no degenerate faces. Dimensions are
248 x 156 x 5 mm (chassis), 42 x 66 x 32.6 mm (cartridge) and 38 x 60 x 6 mm
(adapter). The reviewed PNG is an assembly preview, not a final hand model.

Optional camera packages were installed locally under ignored `.tools/camera-deps`.
MediaPipe 1.2.3, cv2 5.0.0 and NumPy 2.2.6 import successfully, and the application's
HandLandmarker VIDEO options instantiate. Requirements now use one OpenCV
provider, opencv-contrib-python 5.0.0.93. No model inference or live camera test
was performed; model weights are not included. See `models/README.md`.

## Current constraints

- Physical servo, horn, insert and tendon measurements are pending. Provisional
  CAD and pulse endpoints must be reconciled with the actual hardware.
- Bambu Studio was visible in app inventory, but launching it returned
  `Computer Use was not approved to use Bambu Studio`. App permission must be
  enabled by the user before a UI slicing check can be performed.
- FSR-band acquisition, fingertip sensing, grip control, complete hand geometry,
  arm actuation/feedback, IK and autonomous grasping remain future stages.
- Training logs currently contain commands and latest asynchronous telemetry;
  they are not complete synchronized demonstration episodes.

## Next bench session

1. Measure a servo and horn using `MEASUREMENTS.md`.
2. Update the SCAD dimensions and pulse/calibration parameters.
3. Select actual PETG in the slicer and print a fit coupon/pulley before the full rig.
4. Commission one unloaded servo, then one tendon and one finger.
5. Record current, usable travel, return behavior and actual mass before extending
   to the complete hand or choosing arm actuators.

Keep the original 3MFs as supplied references. Use fresh exports after CAD edits.
No printed part or software watchdog replaces a physical power disconnect.
