# Measurement worksheet

No hardware measurements were available during the initial software/CAD pass.
Record actual values in `config/measurements.json`; its planning defaults are
estimates and do not authorize a final print or actuator purchase.

## Servo and horn

Measure one servo first, then check variation across all seven.

| Measurement | Method | Drives |
| --- | --- | --- |
| Case length, width and height | Calipers; exclude shaft/horn | Body clearance and tray height |
| Case bottom to underside of mounting tabs | Calipers | Pillar height |
| Tab thickness and hole spacing in both directions | Calipers | Retaining bolts and inserts |
| Shaft axis offset from nearest case end | Calipers | Pulley and guide alignment |
| Mounted horn top above servo case | Assemble stock horn, measure | Tendon plane |
| Horn diameter, thickness, screw-hole circle and screw size | Calipers and stock screws | Pulley interface |
| Usable pulse endpoints and corresponding angle | Unloaded servo, angle template; approach gradually | Firmware mapping |
| Rotation between usable endpoints | Angle template/video | Effective pulley radius |
| Actual servo mass and loaded current | Scale; current-limited bench test | Mass and power budgets |

Do not force a horn against a stop to determine travel. The manufacturer lists
159 degrees for its positional MG996R, which is a warning against assuming
180 degrees, not a guarantee for the particular units on your bench.
[Manufacturer source](https://towerpro.com.tw/product/mg996r/).

## Tendon path and printed fits

| Measurement | Method | Drives |
| --- | --- | --- |
| Tendon diameter | Measure actual line; braid compresses | Groove and guides |
| Pull from fully open to full curl | Pull a single finger manually with a ruler | Pulley radius |
| Pull force throughout motion | Spring scale/load cell | Servo load and routing quality |
| Elastic force at open and fully curled | Measure separately | Return reliability and flexor load |
| Insert OD, length and recommended pilot | Actual hardware/vendor data + coupon | Heat-set pockets |
| PTFE tube OD/ID | Actual stock + fit coupon | Guide hole and retention |
| Printed hole/slot deviation | Small coupon in chosen PETG profile | Clearance compensation |
| PCA9685 and ESP32 board mounting holes | Actual board | Replaceable electronics carrier |

Change one fit parameter at a time. Test the pulley/horn and a mounting coupon
before spending material on the whole forearm.

## Before designing the arm

Weigh the assembled hand, forearm, electronics, wires and payload separately.
Balance each assembly on a rod to locate its center of mass. Record link lengths
and the furthest intended payload reach. Shoulder and elbow torque must include
every downstream mass; the PRD's approximate torque figures are not final sizes.

The elbow interface must be paired with the chosen shaft, bearing arrangement,
fasteners and load path. A bolt pattern and a hole alone do not establish a
structurally qualified elbow.
