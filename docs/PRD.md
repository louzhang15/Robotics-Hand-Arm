# Robotic Hand — PRD

16 Nov 2026 · @Louis Zhang

## Summary and goals

A 3D-printed, tendon-driven robotic hand that mirrors the user's hand from a forearm sensor band, built so the same hardware later accepts webcam control, bolts onto a robotic arm, and runs an ML policy that picks up objects. Full engineering detail (code, wiring, print settings) lives in the companion Robotic Hand — Scalable Build Plan.

End goal: an arm + hand that sees an object with a camera and picks it up on its own.

### Goals

1.  A 5-finger hand (plus wrist or thumb opposition) that opens, closes and holds poses on command.
2.  Control from a forearm pressure-sensor (FSR) band, then from a webcam, with no firmware change between them.
3.  A forearm that becomes the arm's forearm: an elbow and shoulder bolt on later without redesigning the hand.
4.  Data logging from day one, so band, camera and robot data can train ML models.
5.  A portfolio-grade project documented end to end.

Core design rule: the hand only ever receives a vector of normalized joint targets (0.0 open → 1.0 curled). Every input source (sliders, band, camera, ML policy) is a plug-in on the PC that produces that vector.

## Scope

### In scope

- Tendon-driven hand + forearm (InMoov or Aero Hand Open base, custom forearm), 6–7 MG996R servos, ESP32-S3 + PCA9685
- Executor firmware with safety limits; Python PC software with slider, band and camera inputs
- 8-FSR forearm band on its own ESP32, gesture recognition, then camera-labelled regression to finger positions
- Webcam hand mirroring with MediaPipe
- Fingertip contact sensing and grip-current sensing
- A 3–4 joint arm (base yaw, shoulder, elbow) with position feedback, kinematics and camera calibration
- Vision-based grasping: scripted first, then a learned policy

### Out of scope (for now)

- Individual finger joint actuation (one tendon per finger; joints are coupled)
- Finger abduction (spreading) beyond what the base hand design gives
- Untethered battery operation
- Mobile base or two arms

### Non-goals

- A medical or prosthetic device. This is a research and portfolio robot, not something worn or used near people's faces.
- Matching human strength or speed.

## Functional requirements

| ID | Requirement | Verified by |
| --- | --- | --- |
| **Hand hardware** |  |  |
| H1 | Each finger flexes fully and returns open under elastic tension | Slider test, all 5 fingers |
| H2 | Wrist rotation (or thumb opposition) on a 6th servo; 7th servo optional for both | Slider test |
| H3 | Tendon tension adjustable without re-threading (tensioner per tendon) | Re-calibrate one finger in < 5 min |
| H4 | Forearm carries a standard elbow interface (bolt pattern + bearing seat) and cable pass-through ≥ 15 mm | CAD review |
| H5 | Fingertip pockets for thin FSRs and a wiring channel per finger | CAD review |
| **Firmware (ESP32-S3)** |  |  |
| F1 | Accepts cmd JSON lines over USB serial at 115200 baud with 6+ joint values in [0, 1] | Serial test |
| F2 | Clamps every value to [0, 1] and to per-joint calibrated angle limits | Send out-of-range values |
| F3 | Limits each joint's speed (max 0.04 per 20 ms tick by default) | Scope / video |
| F4 | Eases all fingers open if no cmd for 500 ms | Unplug USB mid-grip |
| F5 | cal sets per-joint limits at runtime; relax stops PWM | Serial test |
| F6 | Streams tel telemetry at 10 Hz | Python reader |
| **PC software (Python)** |  |  |
| P1 | Hand class is the only code that talks to hardware | Code review |
| P2 | Slider app controls and calibrates every joint at 20 Hz | Manual |
| P3 | Camera app mirrors finger curls from MediaPipe landmarks with smoothing | Live test |
| P4 | Band app classifies ≥ 4 gestures, later regresses 8 FSR values to joint values | Accuracy test |
| P5 | Every input app can log (timestamp, source, q, band_raw, telemetry) to CSV | File inspection |
| **Sensor band** |  |  |
| B1 | 8 FSRs around the forearm on a separate ESP32, streaming to the PC | Live plot |
| B2 | Band position repeatable between wearings (marks or fixed strap) | Re-wear test |
| **Arm (later)** |  |  |
| A1 | Base yaw, shoulder pitch, elbow pitch; optional forearm roll | Assembly |
| A2 | Every arm joint reports its real position (bus servo or encoder) | Telemetry |
| A3 | cmd gains an a field: arm joint angles in radians | Serial test |
| A4 | URDF model + inverse kinematics reach a commanded fingertip position | Within 1 cm |
| A5 | Camera-to-robot calibration via ArUco marker | Touch a located object within 1.5 cm |
| **Grasping (end goal)** |  |  |
| G1 | Hand stops closing on fingertip contact | Holds a paper cup without crushing |
| G2 | Arm picks up objects located by an overhead camera | 3 different objects, anywhere in workspace |

## Non-functional requirements

| ID | Category | Requirement |
| --- | --- | --- |
| N1 | Safety | Physical e-stop cuts arm motor power; firmware soft limits on every joint; fail-safe open on lost commands |
| N2 | Power | Servo rail separate from logic power; common ground; 1000 µF capacitor on PCA9685 V+; hand rail 6V ≥ 10A |
| N3 | Latency | Camera → hand under 200 ms end to end (other builds report 100–150 ms) |
| N4 | Weight | Hand + forearm ≤ 1,000 g (sets the shoulder torque) |
| N5 | Torque margin | Arm joints sized at 2× static gravity torque (shoulder ~110 kg·cm, elbow ~35 kg·cm at the assumed geometry) |
| N6 | Repeatability | Same command gives the same finger angle within a few degrees across sessions (low-friction tendon routing, tensioners) |
| N7 | Printability | All parts print on a Bambu A1 (256 mm cube) in PETG without supports where possible |
| N8 | Modularity | Swapping the input source never requires reflashing the hand |
| N9 | Data | All runs loggable to CSV with timestamps for ML training |
| N10 | Cost | Hand phase within the existing ~$200 parts + a ~$100 add-on order (power, band, line) |

## System design summary

Architecture: inputs (sliders, FSR band, webcam, ML policy) → PC brain in Python (turns any input into joint targets, logs data) → hand on ESP32-S3 (clamps, rate-limits, drives PCA9685 → servos, streams telemetry back). The arm adds a second driver on the PC side (bus-servo adapter or stepper drivers).

Protocol (JSON lines, USB serial 115200):

| Message | Direction | Example |
| --- | --- | --- |
| cmd | PC → hand | {"t":"cmd","q":[0,0.8,0.8,0.8,0.8,0.5]}; arm later adds "a":[0.0,0.6,-1.2] (radians) |
| cal | PC → hand | {"t":"cal","j":1,"min":30,"max":150} |
| relax | PC → hand | {"t":"relax"} |
| tel | hand → PC | {"t":"tel","q":[…],"ms":12034} |

Joint order (7): thumb flex, thumb opposition, index, middle, ring, pinky, wrist on PCA9685 channels 0–6; channels 7–15 spare for the arm or extras.

## Decisions taken

| Decision | Choice | Why |
| --- | --- | --- |
| Actuation | Tendons + elastic return, servos in forearm | Matches owned parts; keeps the hand light for the arm |
| Controller | ESP32-S3 N16R8 DevKitC-1 as a dumb executor | Logic on the PC means no reflash when inputs change |
| Band sensing | 8-FSR force myography | 91.2% on 48 gestures in published work; cheap; trainable from camera labels |
| Camera tracking | MediaPipe Hands, 21 landmarks | Proven in several identical builds |
| Arm feedback | Bus servos or steppers + magnetic encoders | Kinematics and ML need real joint angles |
| Shoulder actuator | Worm gear, or stepper + cycloidal/planetary, or servo + counterbalance | Standard servos are too weak (InMoov creator's advice) |
| CAD | OpenSCAD via the 3d-print-designer skill; InMoov STLs for fingers/palm | Parametric parts, automated build checks, Bambu 3MF export |
| Reference arm software | LeRobot (SO-101 ecosystem) | Built for imitation learning; SO-101 hardware too weak for this hand (~500 g payload) |

Wiring essentials: ESP32 GPIO 8 → SDA, GPIO 9 → SCL, 3V3 → PCA9685 VCC; avoid GPIO 0, 3, 45, 46, 19, 20 and 35–37. Servo supply → PCA9685 V+ terminal; all grounds common.

## Grasping and ML plan

The hand is designed to grab real objects first and become an ML platform second; both need the same three things: an opposable thumb, contact sensing and clean logged data.

### Grasping requirements

| ID | Grasp | Test object | Needs |
| --- | --- | --- | --- |
| GR1 | Power (whole-hand wrap) | Water bottle, cup | All 5 flexors |
| GR2 | Cylindrical / tool | Marker, screwdriver | Thumb opposition |
| GR3 | Pinch (thumb + index tips) | Coin-sized block, pen cap | Thumb opposition, fingertip pads |
| GR4 | Lateral (thumb on side of index) | Card, key | Thumb opposition |
| GR5 | Soft grip without crushing | Paper cup, sponge | Fingertip FSRs + current sensing |

Decision: add a 7th MG996R for thumb opposition. Wrist rotation alone can't make pinch, tool or lateral grasps; most useful grasps need the thumb to swing across the palm. PCA9685 channel 6 is free, so the joint vector becomes 7 values: thumb flex, thumb opposition, index, middle, ring, pinky, wrist.

Grip quality: print TPU fingertip and palm pads on the A1 (it handles TPU) for friction and compliance; PETG on PETG slips.

### ML ladder (each rung uses the previous one's data)

1.  Band → hand regression (phase 4): supervised learning, camera labels as ground truth. Small MLP or random forest.
2.  Grasp-type selection (phase 6a): camera detects the object, a classifier picks a grasp from GR1–GR5, a scripted reach executes it.
3.  Imitation learning (phase 6b): teleoperate the hand with the band/camera and the arm with a leader arm or camera, record episodes, train a policy such as LeRobot's ACT. Plan on the order of 50 demonstrations per task to start.
4.  Simulation / RL (optional): URDF in MuJoCo or Isaac, train there, fine-tune on real data.

Episode data spec (logged by every run): timestamp; camera frame(s); hand joint targets and telemetry; arm joint angles; band raw values; fingertip forces; task label; success flag. Stored as CSV + image folders, convertible to the LeRobot dataset format.

## Milestones and acceptance criteria

Each phase ends at its gate (the diamond); the next starts only when it passes. Phase 0 runs first: measure servo rotation and horn, print the one-finger test rig, and choose InMoov vs Aero Hand Open.

Phase 5 arm sub-steps: elbow only, lifting hand + 300 g at full extension for 30 s → shoulder + base, holding any pose under 60% rated torque → URDF + IK within 1 cm → ArUco camera calibration within 1.5 cm.

## Bill of materials

### Owned

| Part | Qty | Role |
| --- | --- | --- |
| Bambu Lab A1 | 1 | Printer (PETG and TPU) |
| Overture PETG | 3 spools | Structure |
| TowerPro MG996R | 6 | Finger tendons + wrist |
| PCA9685 (Adafruit-style) | 1 | 16-channel servo PWM |
| ESP32-S3 N16R8 DevKitC-1 | 2 | Hand controller (+ spare for the band) |
| 50 lb braided line | 1 spool | Test tendons only |
| 1 mm elastic cord | 1 | Finger return |
| M3 heat-set inserts | set | Joints, mounts |
| 5V 4A adapter + 5.5 mm barrel adapter | 1 | Logic / bench power (confirm 2.1 vs 2.5 mm plug) |
| 3-pin servo extension cables | 1 pack | Wiring |

### To buy

| Part | Qty | Phase | Why |
| --- | --- | --- | --- |
| 6V 10A (60 W) supply | 1 | 1 | Servo rail with stall headroom |
| 1000 µF 16V capacitor | 2 | 1 | Servo current spikes |
| 100–200 lb braided line (or 0.5–0.8 mm steel leader + crimps) | 1 | 1 | Final tendons; thin line cuts plastic |
| PTFE tube 4 mm OD / 2 mm ID | 1 m | 1 | Low-friction tendon guides |
| Small extension springs | ~10 | 1 | Tendon tension (InMoov-style) |
| MG996R (7th servo) | 1 | 1 | Thumb opposition |
| TPU filament | 1 spool | 1 | Fingertip and palm grip pads |
| FSR 402 | 8 | 2 | Forearm band |
| 10 kΩ resistors, ADS1115 (optional) | 8, 1–2 | 2 | FSR dividers, clean ADC |
| Webcam 720p+ | 1 | 3 | Tracking and data labels |
| Thin fingertip FSRs | 5 | 5 | Contact sensing |
| INA219 current sensor | 1 | 5 | Grip force estimate |
| Arm actuators (worm-gear servos, or steppers + gearboxes + AS5600 encoders + TMC2209 drivers) | 3–4 joints | 5 | Arm, sized after weighing the hand |
| 608 bearings, 8 mm shaft | 4+ | 5 | Elbow and shoulder bearings |
| 12V/24V arm supply + e-stop switch | 1 | 5 | Arm power and safety |

## Risks, open questions and evidence

### Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Servo brownout on a full fist | ESP32 resets | Separate 6V 10A rail, capacitor, common ground, rate limit |
| Thin tendon line | Cuts printed channels | 100–200 lb line or steel leader + PTFE tubes |
| Tendon stretch and friction | Command ≠ finger angle; ML data drifts | Tensioners, springs, PTFE routing, cal re-calibration |
| MG996R travel under 180° | Fingers don't fully curl | Measure first; pulley radius derived from measured angle |
| No position/force feedback in MG996R | Crushes or drops objects | Fingertip FSRs + INA219 |
| FSR accuracy changes with arm pose | Band misreads once the arm moves | Train with data from several arm poses |
| Hand too heavy for the arm | Shoulder stalls | ≤ 1 kg budget, counterbalance, worm gear or geared stepper |
| Arm injures user | Physical harm | E-stop, soft limits, torque limits, slow speeds during tests |

### Open questions

- [ ] Base hand: InMoov vs Aero Hand Open (lighter, ESP32 + ROS2, built for research)
- [ ] Measured MG996R rotation range, horn size, M3 insert size, final line diameter, PCA9685 hole spacing
- [ ] Barrel adapter plug size (5.5 × 2.1 vs 2.5 mm)
- [ ] Arm actuator family: bus servos vs steppers with encoders
- [ ] Compute for untethered use later: Raspberry Pi 5 vs Jetson

### Evidence from existing builds

- InMoov builds use 6 standard servos, 200 lb braided line, springs and tubes on the servo bed (InMoov guide, parts thread).
- InMoov's creator advises against standard servos for the shoulder and bicep (thread).
- An 8-FSR band reached 91.2% on 48 gestures, ahead of a commercial EMG array (PubMed 28161107); limb position strongly affects accuracy (Sensors 2023).
- MediaPipe → ESP32 + PCA9685 hands report 100–150 ms latency (example).
- SO-101 arm: STS3215 servos, ~500 g payload (specs).
- Research hands for robot learning (LEAP, RUKA, ORCA) and Aero Hand Open (375 g, ESP32 + ROS2).

## Deliverables and project package

The project ships as robotic-hand.zip. The 7-joint code in the zip supersedes the 6-joint snippets in the build plan.

| Path | Contents | Status |
| --- | --- | --- |
| docs/PRD.md | This document | Current |
| firmware/hand_executor/hand_executor.ino | ESP32-S3 executor: JSON protocol, 7 joints, calibration, rate limit, fail-safe, telemetry | Starter, untested on hardware |
| pc/hand.py | Hand class + CSV logging | Starter |
| pc/sliders.py | Manual control and per-joint calibration UI | Starter |
| pc/camera.py | MediaPipe mirroring incl. thumb opposition; --dry mode without hardware | Starter, thresholds need tuning |
| pc/requirements.txt | Python dependencies | Current |
| cad/finger_test_rig.scad | Parametric one-finger test rig (servo bed, tendon pulley, guide, anchor, ruler) | Gate passed, Sonnet review fixes applied |
| cad/*.stl, cad/*.3mf | Print files; 3MFs open in Bambu Studio with A1 + PETG settings | Ready after measurements |

## Next actions

- [ ] Order the phase 1 items in the BOM (6V 10A supply, 100–200 lb line, PTFE tube, springs, 7th servo, TPU)
- [ ] Measure: servo rotation, horn diameter and hole radius, case and tab heights, insert size
- [ ] Update the rig parameters, reprint the pulley if needed, run the one-finger test
- [ ] Decide InMoov vs Aero Hand Open, then design the forearm (servo bed for 7, elbow interface)
