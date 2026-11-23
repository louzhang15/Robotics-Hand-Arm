# First arm target: pick up a pen

## Agreed scope

The user confirmed a complete robotic arm with the existing robotic hand,
whose first task is to pick up a pen from the desk and move it elsewhere.
The agreed approximate reach is **30 cm (300 mm)**.

For CAD planning, interpret reach as the horizontal distance from the shoulder
axis to the pen's gripping point. This reference definition is a working
assumption to check when the arm layout is drawn; 300 mm is not the length of
each arm link. The pen's actual mass and dimensions have not been measured.

Start with manual positioning and a repeatable, marked pen location. Camera
localization and autonomous grasping remain later goals from the original PRD.
This initial test does not replace the broader requirements in `PRD.md`.

## First demonstration gate (proposed)

With the base secured and the pen at a marked tabletop location, grasp the pen,
lift it clear of the desk, move it to a second marked location, and release it.
Aim for five consecutive successful attempts. These repetition and placement
details are proposed acceptance criteria, not results or additional user promises.
Record failures, current draw, slipping, binding and actual joint behavior.

## What still determines the arm hardware

A light pen does not make the shoulder load equal to the pen's mass. Joint
sizing must include the complete downstream hand, servo carrier, wrist,
links, wiring, transmissions and payload, with their actual lever arms.
Allow for motion loads, holding duty, thermal limits and a design margin.
No shoulder or elbow actuator rating is selected by this scope agreement.

Before buying the arm drives:

1. Measure the servo/horn interfaces and make the one-finger test fixture fit.
2. Establish a hand/forearm mass and center-of-mass estimate; replace estimates
   with measurements as assemblies are built.
3. Lay out the shoulder, elbow, wrist and gripping point for the 300 mm target.
   Check tabletop reach, grasp orientation, collisions and base stability.
4. Calculate joint loads, then select actuators with suitable feedback,
   transmissions, matching drivers, power distribution and an emergency stop.
5. Qualify the elbow with a representative measured load before integrating
   the shoulder/base and hand.

Keep the owned MG996Rs assigned to hand development for now. Their suitability
for larger arm joints has not been established. The existing **5 V / 4 A**
adapter is nameplate-confirmed from the user's photo; its delivered output,
connector fit and polarity have not been measured. It is not the selected
supply for the complete arm and hand.

## Immediate tools and next physical step

The user has wires and no multimeter. Prioritize a multimeter with DC-voltage
and continuity modes, calipers for mechanical fits, and suitable small
screwdrivers/hex keys. Confirm the existing wires' connector ends before
buying more. A soldering iron is deferred while preterminated connections suffice.

The next bring-up step is the ESP32 alone over a USB data cable, with the
PCA9685, external adapter and servos disconnected. External-power commissioning
waits for measured voltage/polarity and checked wiring. No hardware readiness
or physical test pass is implied by this document.
