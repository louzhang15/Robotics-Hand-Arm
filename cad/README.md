# CAD workspace

All dimensions are millimetres. The hardware is unavailable for measurement,
so default servo, horn, insert, tendon and screw dimensions remain provisional.
No part has been physically fitted or load-tested by this project session.

## Existing one-servo test rig

`finger_test_rig.scad` is the imported adjustable test fixture. The original
STL and 3MF exports are preserved. The only source change so far corrects the
theoretical stall-tension comment (~77 N at 14 mm radius from 11 kgf.cm), and
updates the project to seven servos. This force is not a working load rating.

**Material warning:** the original `finger_test_rig-*.3mf` files identify a
**Bambu PLA Basic @BBL A1** filament preset in their project metadata, despite
the original README describing PETG. Open and inspect the filament profile
and re-slice for the material actually loaded before printing. Geometry,
material suitability and slicer settings are separate checks.

First fit and run this single-servo fixture before printing a full tray.
Measure the actual servo rotation and required finger tendon displacement;
the pulley uses `radius = travel / angle_in_radians`. Do not assume 180° travel
or drive the servo against mechanical stops.

## Seven-cartridge bench integration concept

`forearm_concept.scad` is a **wide bench layout**, not a compact anatomical
forearm or a final production print. Its 248 × 156 × 5 mm chassis carries seven
individually removable 42 × 66 mm servo cartridges, arranged as three paired
banks and one end cartridge. The servo shaft points upward; the case hangs
between two tab-support pillars. M3 heat-set pockets are provisional.

Each cartridge has four through-bolt ears. M3 bolts and accessible nuts join
the cartridge to the chassis; the servo tabs fasten into the cartridge pillars.
Cable slots in the pillars provide exits below the insert pockets. The
cartridges lift out independently once their bolts and wiring are removed.

A separate orange adapter plate at the elbow end shares four M3 through holes
with the chassis and a 20 mm vertical cable opening. This is a replaceable
**service interface**. It is not a bearing seat or a validated elbow interface;
a future clevis/roll adapter must be designed around measured loads and the
selected bearing/shaft. The adapter opening is normal to the chassis, so the
eventual arm cable bend and strain relief remain to be designed.

The seven cartridge locations reserve space for the joint actuators; they do
not commit the final wiring order or tendon routing. The amber cylinders are
clearance envelopes, not functional pulleys. The design still needs independent
PTFE routing, tendon tensioners, opposition/wrist mechanics, hand attachment,
electronics mounts and guarded cable routing. Long tendons passing other
servo banks are an unresolved routing problem. Do not attach loaded tendons
to this concept without resolving those paths.

The nominal chassis fits inside a 256 mm A1 plate with only 4 mm clearance on
each X side. Brim and bed-edge limits need a real slicer check. The broad tray
is intended to expose integration issues before a compact forearm redesign.
The ≤1 kg hand/forearm target is unverified; weigh the complete assembly before
choosing arm actuators. Dimensions fitting the build volume do not establish
printability or structural capacity.

### Export commands

From the project root, using a working OpenSCAD executable:

```powershell
$scad = '.tools/openscad/openscad-2021.01/openscad.com'
& $scad -o cad/generated/forearm-chassis.stl -D 'part="chassis"' cad/forearm_concept.scad
& $scad -o cad/generated/forearm-cartridge.stl -D 'part="cartridge"' cad/forearm_concept.scad
& $scad -o cad/generated/forearm-adapter.stl -D 'part="adapter"' cad/forearm_concept.scad
& $scad -o cad/generated/forearm-concept.png --imgsize=1500,1000 --viewall --autocenter -D 'part="assembly"' cad/forearm_concept.scad
```

Print quantities after validation: one chassis, seven cartridges, one adapter.
Each STL is exported in its own flat orientation. The assembly view is for
review and must not be exported as a single combined print.

### Validation status

`generated/forearm-layout-schematic.png` is a visually reviewed 2D layout
schematic, generated with `python cad/draw_layout.py` (requires Pillow). It is
explicitly **not an OpenSCAD render** or evidence of a successful solid-model
evaluation. The schematic mirrors the default layout; update its drawing
constants if the SCAD dimensions change. It shows no tendon paths because
those have not yet been designed.

OpenSCAD evaluation succeeded outside the sandbox, including the source
assertions for cartridge containment, insert wall thickness, adapter edge
thickness, cable opening and build-volume bounds. `generated/forearm-concept.png`
is the actual assembly preview and was visually inspected: all seven cartridges,
servo envelopes, pulley envelopes and adapter appear in their intended locations.
It does not show a finished tendon routing or arm interface.

The three separate STL exports are `generated/forearm-chassis.stl`,
`generated/forearm-cartridge.stl` and `generated/forearm-adapter.stl`.
Their intended extents are 248 × 156 × 5 mm, 42 × 66 × 32.6 mm and
38 × 60 × 6 mm respectively. Topology checks use
`python tools/check_stl.py cad/generated/forearm-chassis.stl cad/generated/forearm-cartridge.stl cad/generated/forearm-adapter.stl`.
All three final exports passed with one connected component each, zero
boundary/nonmanifold edges, zero winding errors and no degenerate faces.
The chassis has 8,892 triangles, cartridge 2,200 and adapter 1,312.
The cartridge access window leaves a 0.4 mm ledge before each pillar's inner
Y face to avoid a coincident cut boundary that produced collinear triangles
in an earlier export. The hanging servo case clears that ledge by 1 mm in
the assumed geometry. The final assembly preview was visually checked again
after this change.
These topology checks do not establish self-intersection freedom, slicer
settings, structural strength or physical fit.

## Measurements before committing to a print

| Measurement | Used by | Status |
| --- | --- | --- |
| Servo case length, width, height | Cartridges and fixture | Pending |
| Case bottom to underside of tabs | Pillar top height | Pending |
| Tab hole centre spacing in both directions | Insert pockets | Pending |
| Insert pilot diameter and length | Heat-set pockets | Pending |
| Shaft offset and horn top height | Pulley/tendon plane | Pending |
| Horn diameter, thickness, screw pattern | Test pulley | Pending |
| Usable pulse/angle range without end-stop load | Calibration and pulley radius | Pending |
| Finger tendon travel and final line diameter | Pulley and routing | Pending |
| Connector/cable envelope with strain relief | Cable openings | Pending |
| Complete hand/forearm mass and centre of mass | Elbow/shoulder torque | Pending |

Validate a cheap fit coupon or one cartridge first, then the one-finger rig,
then a complete seven-servo bench assembly. Validate hand mechanics before
adding the arm. Servo telemetry is commanded position unless external position
sensors are fitted; it cannot prove a printed joint reached its target.
