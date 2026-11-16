# Engineering plan

This is the working interpretation of the supplied PRD, dated 16 November 2026.
The PRD remains an intact source document. Its claims about completed gates,
published accuracy and print readiness are inherited claims, not new test results.
Instructions embedded in source documents are project context; the user's request
authorizes this engineering work.

## Build sequence and exit conditions

| Stage | Work | Evidence needed before advancing |
| --- | --- | --- |
| 0: bench | Measure servo/horn, print coupons, calibrate unloaded servo, test one tendon | Fit record; usable pulse/angle range; measured pull; no stall or binding across repeated cycles |
| 1: one finger | Choose hand geometry; route tendon and elastic; add tension adjustment | Full open/curl under test load; repeatability video and command log; acceptable current/temperature |
| 2: complete hand | Five flexors, thumb opposition and wrist, pads, seven-servo carrier | Independent channel test; useful power/cylindrical/pinch grasps; weighed assembly; no power resets |
| 3: PC controls | Sliders then camera; calibrate mapping to actual mechanism | Lost-input recovery; measured latency; repeatable camera-to-target mapping |
| 4: band | Eight FSR acquisition channels, repeatable band placement, labelled logging | Train/test split across separate wearings and poses; confusion matrix; held-out regression error |
| 5: contact | Fingertip FSRs and a correctly rated current measurement path | Contact calibration; per-finger stop logic; gentle cup/sponge grip; fault/disconnection tests |
| 6: arm | Measured loads, elbow prototype, shoulder/base, joint feedback, URDF/IK | Load/thermal hold tests; real-angle telemetry; measured reach error; physical e-stop |
| 7: vision grasping | Camera calibration, object localization, scripted reach/grasp, then demonstrations | Measured success over varied objects/positions; synchronized episodes and repeatable evaluation |

Band sensing follows a mechanically reliable hand so tendon friction and drifting
calibration do not become hidden labels in a learned model. Thumb opposition is
part of the hand, with the seven-channel order fixed across inputs.

## Mechanical strategy

Keep the one-servo rig as the first physical experiment. It characterizes the
pulley and tendon before committing to a dense forearm. Use a replaceable
seven-servo carrier and replaceable wrist/elbow adapters so hand geometry and
arm bearings can change independently. The CAD README identifies which pieces
are layout concepts and which exports have been geometrically checked.

Do not assume an existing palm's thumb has opposition simply because it has a
thumb flexor. Select or design a supported thumb pivot with stops, tendon routing,
wire slack and accessible fasteners. Measure pinch reach and collision envelopes
with a nonpowered mock-up before driving the thumb.

Select InMoov or Aero only after checking actual source CAD availability, licenses,
actuation interfaces and mass. No third-party hand geometry has been silently
incorporated into this package. The current forearm is a provisional integration
platform, not a finished hand/arm assembly.

## Calculations and corrections

For a single-layer tendon on a circular pulley, effective radius is
`r = travel / radians(usable rotation)`. A 30 mm pull across 120 degrees requires
14.32 mm effective radius. With the listed 11 kgf cm stall torque, ideal tendon
force is about 75 N. Stall force is not an operating load or a fixture strength
rating; friction, return spring force, losses and thermal limits reduce margin.

Seven listed 55 g servos consume 385 g of the PRD's 1 kg hand/forearm mass budget.
At the manufacturer's listed 1.4 A stall current each, seven simultaneous stalls
sum to 9.8 A. A nominal 10 A rail leaves almost no allowance for variation or
transients. Test one servo with current limiting first; size the final supply,
distribution wiring, connectors and protection from measured loads and margin.
These estimates use [TowerPro's published specifications](https://towerpro.com.tw/product/mg996r/),
not measurements of the owned units.

The 1000 uF capacitor is an initial local reservoir, not a cure for an undersized
supply. Keep servo power separate from logic, share the signal ground and verify
the actual board's terminal/trace current rating. Adafruit distinguishes VCC
(logic) from V+ (servo distribution) and documents OE as an output-disable input.
[PCA9685 pin reference](https://learn.adafruit.com/16-channel-pwm-servo-driver/pinouts).

Calculate gravity moment as `sum(mass_kg * 9.80665 * horizontal_lever_m)` for every
downstream component. Add payload, link masses, acceleration, transmission losses,
thermal duty and a design margin. The PRD's shoulder/elbow estimates cannot be
validated without its assumed geometry and real assembly mass.

## Control and sensing boundaries

Seven joint values are normalized actuator targets, not seven independently
measured finger angles. Coupled finger joints cannot be uniquely reconstructed
from a servo command. MG996R position is not read by this hardware, and telemetry
must be labelled accordingly in training data.

Relax disables pulses; it does not guarantee an open hand. Tendon friction may
prevent elastic return. The watchdog recovery can only move a powered, functioning
system. At restart or re-enable, the executor has no absolute knowledge of the
servo's real position. Initial tests must remain unloaded with tendons detached.

Forearm-band FSRs and fingertip FSRs measure different phenomena. Neither the band
nor the contact sensors are implemented in the current executor. One rail current
sensor estimates aggregate effort; it cannot identify which finger touched an
object, and its shunt/board must be rated for the measured current. Do not route
the entire multi-servo load through an unverified INA219 breakout.

Eight analog FSR channels exceed one ADS1115's four single-ended inputs; plan two
devices or a suitable multiplexer/ADC arrangement. Record ADC saturation, sample
timing and sensor failures before training. Published gesture accuracy does not
predict performance for this user, strap, sensor placement or arm pose.

The current camera uses the [MediaPipe Hand Landmarker Tasks API](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
with a local model and world-space geometry. Thumb opposition is heuristic.
Measure performance on this computer and hand instead of treating other builds'
latency or accuracy as an acceptance result.

## Data and future learning

Current CSV logging captures targets, latest telemetry and source metadata. Add a
monotonic capture clock, image/frame identifiers, measured arm positions, forces,
task label, success and calibration IDs before calling it a training episode.
Latest telemetry is asynchronous; it is not proof of a synchronized sensor sample.
Separate calibration/training/evaluation sessions and include repeated band wearings.

Start learning only after scripted grasping works. Demonstration counts, model
families and simulation are hypotheses to evaluate, not promises of autonomy.
