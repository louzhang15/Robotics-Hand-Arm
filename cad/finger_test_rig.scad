// === DESCRIPTION ===
// Finger test rig: a bench fixture for ONE MG996R servo pulling ONE tendon,
// built to measure servo travel, tendon stretch and pulley sizing before the
// full seven-servo forearm of the Robotic Hand project is designed.
//
// Physical context: bolts to a bench or board through 4 corner holes. The
// MG996R hangs between two pillars by its mounting tabs (shaft pointing up),
// screwed into M3 heat-set inserts. The tendon pulley screws onto the servo's
// round disc horn. The braided tendon wraps the pulley groove, leaves along +X,
// passes through a PTFE guide tube in the guide tower, and ends at the anchor
// post, where 1mm elastic cord gives the return tension a finger's extensor
// would. Tick marks on the plate (every 5mm, long every 10mm) measure travel.
// Loads: 11 kgf.cm / ~14mm gives ~77 N theoretical STALL tendon tension.
// This is NOT a continuous rating or a validated printed-fixture load rating.
// Begin with low tendon tension; pillar/tower loads act mainly in the XY plane.
//
// Design decisions:
//   - Servo shaft vertical so the pulley and tendon run parallel to the plate;
//     every printed load runs along the layers.
//   - Servo hangs on its tabs with 1mm under the case, so the tabs (not the
//     case bottom) locate it, as in a real servo bed.
//   - Pulley radius is DERIVED from the wanted tendon travel and the servo's
//     usable rotation: r = travel / angle(rad). Change those two numbers once
//     the real servo is measured and reprint the pulley only.
//   - Guide and anchor heights are derived from the servo/horn heights so the
//     tendon runs level.
//   - V groove with 45 degree flanks so the pulley prints flat with no support.
//
// Terminology -> code:
//   "servo bed" / "base"   -> base(), plate_l, plate_w, plate_t
//   "pillars"              -> pillar(), pillar_w, servo_gap
//   "servo inserts"        -> insert_hole_d, insert_len, tab_hole_spacing_l/_w
//   "pulley" / "spool"     -> pulley(), tendon_travel, servo_range_deg, r_eff
//   "horn"                 -> horn_d, horn_t, horn_hole_r, horn_screw_d
//   "guide tower" / "tube" -> guide_tower(), tube_od, guide_x
//   "anchor post"          -> anchor_post(), anchor_x
//   "ticks" / "ruler"      -> ticks(), tick_pitch
//
// Common modifications (MEASURE FIRST, then edit):
//   Real servo rotation      -> servo_range_deg (pulley radius follows)
//   Finger tendon travel     -> tendon_travel (InMoov index ~25-30mm, estimate)
//   Horn size / screw holes  -> horn_d, horn_t, horn_hole_r, horn_hole_n
//   Horn top height          -> servo_case_h + horn_above_case (horn_top_h derived)
//   Tab height               -> tab_bottom_h (case bottom to underside of tabs)
//   Insert size              -> insert_hole_d, insert_len (datasheet first)
//   Tube size                -> tube_od (PTFE 4mm OD default)
//
// Overall dimensions: base 220 x 70 x ~68 mm; pulley ~34 dia x 12.5 mm.
//   Fits Bambu A1 (256 x 256 x 256).
// Coordinate system: X = tendon direction, Y = servo length, Z = up from plate.
// NOTE: Model is in print orientation; preview matches the print.
// Final review: 2026-11-16, claude-sonnet-5-5 (code-only); findings 1-9 fixed.

// === PRINT SETTINGS ===
// Material: PETG (ductile, good layer bond; takes heat-set inserts at 200-220 C)
// Layer Height: 0.2mm
// Walls/Perimeters: 4 (1.8mm)
// Infill: 30% gyroid (pillars hold inserts: 4 walls carry them)
// Supports: None required (V groove 45 degree flanks, teardrop tube holes)
// Orientation: base flat on plate; pulley flat, horn pocket UP (flipped in use).
// Notes: nozzle 240 C, bed 70-80 C textured PEI, fan 30-40%. Dry PETG if it pops.

// === PARAMETERS ===
nozzle_diameter = 0.4;
layer_height = 0.2;

// Servo (TowerPro MG996R typical values: VERIFY with calipers)
servo_l = 40.7;            // case length (along Y)
servo_w = 19.7;            // case width (along X)
tab_bottom_h = 26.6;       // case bottom to underside of mounting tabs (VERIFY)
tab_hole_spacing_l = 49.5; // tab hole centres along length (VERIFY)
tab_hole_spacing_w = 10.0; // tab hole centres across width (VERIFY)
shaft_from_end = 10.2;     // shaft axis to near case end (VERIFY)
servo_case_h = 42.9;       // case bottom to case top, excluding shaft (VERIFY)
horn_above_case = 4.0;     // case top to top face of mounted round horn (VERIFY)
tab_t = 2.5;               // mounting tab thickness (VERIFY)
tab_overhang = 6.9;        // tab length beyond each case end (VERIFY)
cable_notch_w = 10;        // servo cable exit through the pillar base
cable_notch_h = 6;
servo_drop = 1.0;          // gap under the case so the tabs locate the servo

// Horn (round disc horn from the servo kit: VERIFY)
horn_d = 25.0;
horn_t = 2.5;
horn_hole_r = 8.5;         // radius of the horn screw holes used
horn_hole_n = 4;
horn_screw_d = 2.0;        // small screws through pulley into horn holes
horn_centre_screw_head_d = 6.0;
horn_screw_head_d = 4.0;   // counterbore for the small horn screws
horn_screw_floor = 3.0;    // material left under the counterbore

// Tendon / pulley
tendon_travel = 30;        // mm of tendon pull for a full curl (estimate)
servo_range_deg = 120;     // usable rotation (conservative until measured)
line_d = 0.8;              // 200 lb braid ~0.8mm
groove_depth = 3.0;
pulley_floor = 3.0;        // solid floor above the horn pocket
pocket_depth = 1.5;        // centring pocket over the horn disc
top_flange = 2.0;
tie_hole_d = 1.8;

// Inserts (M3 heat-set: VERIFY against datasheet)
insert_hole_d = 4.0;
insert_len = 5.7;

// Base
plate_l = 220;
plate_w = 70;
plate_t = 5;
corner_r = 6;
mount_hole_inset = 7;
m3_clear = 3.6;            // M3 + hole comp 0.30 + free 0.30
pillar_w = 22;             // along X
pillar_d = 12;             // along Y

// Guide tower and anchor
tube_od = 4.0;             // PTFE tube
tube_len_in_tower = 14;
guide_gap = 30;            // pulley edge to guide tower
anchor_x_from_end = 10;
elastic_max_stretch = 1.5;  // (rest + travel) / rest for 1mm elastic cord
tick_pitch = 5;
tick_depth = 0.6;

// === DERIVED CONSTANTS ===
extrusion_width = nozzle_diameter * 1.125;
wall_thickness = extrusion_width * 4;
fudge = 0.01;
tolerance = 0.3;           // PETG sliding fit
hole_comp = 0.30;
ef_chamfer = 0.4;
$fn = $preview ? 32 : 64;

r_eff = tendon_travel / (servo_range_deg * PI / 180);  // tendon centreline radius
r_root = r_eff - line_d * sqrt(2) / 2;                  // line seats this far up a 90 deg V
r_rim = r_root + groove_depth;
pulley_h = pocket_depth + pulley_floor + 2 * groove_depth + top_flange;
groove_z_in_pulley = pocket_depth + pulley_floor + groove_depth;  // groove centre

servo_x = 40;                                     // servo centre along X
servo_y = plate_w / 2;                            // servo centre along Y
servo_bottom_z = plate_t + servo_drop;
horn_top_h = servo_case_h + horn_above_case;    // case bottom to horn top face
shaft_y = servo_y + servo_l / 2 - shaft_from_end; // shaft near +Y end
pulley_bottom_z = servo_bottom_z + horn_top_h - pocket_depth;
tendon_z = pulley_bottom_z + groove_z_in_pulley;
tendon_y = shaft_y - r_eff;                       // leaves the -Y side of pulley along +X
pillar_top_z = servo_bottom_z + tab_bottom_h;
guide_x = servo_x + r_rim + guide_gap;
anchor_x = plate_l - anchor_x_from_end;
tube_hole_d = tube_od + hole_comp - 0.08;          // press fit so the tube can't walk
tower_w = tube_hole_d + 2 * 4;                     // along Y, at the top
foot_w = 30;                                       // along Y, at the plate (stability on a bed-slinger)
tower_l = tube_len_in_tower;                       // along X

// === CONTRACTS ===
assert(r_root - (horn_hole_r + (horn_screw_head_d + hole_comp) / 2) >= 1.6, "groove root too close to the screw counterbores");
assert(horn_hole_r + horn_screw_d / 2 < horn_d / 2, "horn screws must land on the horn");
assert(horn_centre_screw_head_d / 2 < horn_hole_r - horn_screw_d / 2 - 0.8, "centre hole hits horn screws");
pillar_inner_wall = (tab_hole_spacing_l - servo_l) / 2 - tolerance - insert_hole_d / 2;
assert(pillar_inner_wall >= 1.6, "insert too close to the pillar's inner face");
assert(pillar_top_z - insert_len - 1 > plate_t, "insert pocket must fit in the pillar");
assert(tendon_y - tower_w / 2 > 0, "guide tower off the plate");
assert(guide_x + tower_l / 2 < anchor_x - 10, "guide and anchor overlap");
assert(abs(r_eff * servo_range_deg * PI / 180 - tendon_travel) < 1e-6, "pulley radius gives the wanted travel");
elastic_rest = anchor_x - 5 - (guide_x + tower_l / 2 + 8);   // tower exit to anchor tie point
assert((elastic_rest + tendon_travel) / elastic_rest <= elastic_max_stretch, "elastic span too short for the travel");
assert(pulley_bottom_z - (servo_bottom_z + servo_case_h) >= 1.5, "pulley must clear the servo case top by 1.5mm");
assert(pillar_top_z - insert_len - 1 > plate_t + cable_notch_h + cable_notch_w / 2, "cable notch reaches the insert pockets");
assert(pulley_h - pocket_depth - horn_screw_floor > 2, "counterbore leaves too little");
echo(elastic_rest = elastic_rest, horn_screw_len_min = horn_screw_floor + horn_t,
     pulley_case_clearance = pulley_bottom_z - (servo_bottom_z + servo_case_h));
echo(pulley_effective_radius = r_eff, pulley_outer_d = 2 * r_rim, tendon_height = tendon_z,
     pillar_inner_wall = pillar_inner_wall);

// === MODULES ===
module rounded_plate(l, w, t, r) {
    // elephant-foot chamfer on the bottom edge
    hull() for (x = [r, l - r], y = [r, w - r]) translate([x, y, 0]) {
        translate([0, 0, ef_chamfer]) cylinder(r = r, h = t - ef_chamfer);
        cylinder(r = r - ef_chamfer, h = ef_chamfer + fudge);
    }
}

module teardrop_hole(d, h, axis = "y") {
    r = d / 2;
    rotate([0, 0, axis == "x" ? 90 : 0]) rotate([90, 0, 0])
        linear_extrude(height = h, center = true)
            union() { circle(r = r); rotate(45) square(r); }
}

module pillar(sign) {
    // sign = +1 (+Y end) or -1 (-Y end)
    y0 = servo_y + sign * (servo_l / 2 + tolerance);
    yc = y0 + sign * pillar_d / 2;
    hole_y = servo_y + sign * tab_hole_spacing_l / 2;
    difference() {
        translate([servo_x - pillar_w / 2, yc - pillar_d / 2, plate_t - fudge])
            cube([pillar_w, pillar_d, pillar_top_z - plate_t + fudge]);
        // cable exit: notch through the pillar base, 45-degree roof (self-supporting)
        translate([servo_x, yc, plate_t]) rotate([90, 0, 0])
            linear_extrude(height = pillar_d + 2 * fudge, center = true)
                polygon([[-cable_notch_w / 2, -fudge], [cable_notch_w / 2, -fudge], [cable_notch_w / 2, cable_notch_h],
                         [0, cable_notch_h + cable_notch_w / 2], [-cable_notch_w / 2, cable_notch_h]]);
        for (dx = [-1, 1] * tab_hole_spacing_w / 2)
            translate([servo_x + dx, hole_y, pillar_top_z - insert_len - 1])
                cylinder(d = insert_hole_d, h = insert_len + 1 + fudge);
    }
}

module guide_tower() {
    h = tendon_z + tube_hole_d / 2 + 5;
    difference() {
        // tapered tower: 30mm-wide foot in Y and X flare for stability; taper is well under 45 degrees
        hull() {
            translate([guide_x - tower_l / 2 - 8, tendon_y - foot_w / 2, plate_t - fudge])
                cube([tower_l + 16, foot_w, 1]);
            translate([guide_x - tower_l / 2, tendon_y - tower_w / 2, plate_t - fudge])
                cube([tower_l, tower_w, h - plate_t]);
        }
        translate([guide_x, tendon_y, tendon_z])
            teardrop_hole(tube_hole_d, tower_l + 16 + 2 * fudge + 2, axis = "x");
    }
}

module anchor_post() {
    h = tendon_z + 6;
    post_l = 10;
    difference() {
        hull() {
            translate([anchor_x - post_l / 2 - 6, tendon_y - foot_w / 2, plate_t - fudge]) cube([post_l + 6 + (anchor_x_from_end - post_l / 2) - 1, foot_w, 1]);
            translate([anchor_x - post_l / 2, tendon_y - 6, plate_t - fudge]) cube([post_l, 12, h - plate_t]);
        }
        // tie hole for the elastic cord, along X at tendon height
        translate([anchor_x, tendon_y, tendon_z]) teardrop_hole(3, post_l + 14, axis = "x");
    }
}

module ticks() {
    x0 = guide_x + tower_l / 2 + 8 + 2;
    for (x = [x0 : tick_pitch : anchor_x - 12]) {
        long = (round((x - x0) / tick_pitch) % 2) == 0;
        translate([x - 0.4, tendon_y - (long ? 8 : 5), plate_t - tick_depth])
            cube([0.8, long ? 16 : 10, tick_depth + fudge]);
    }
}

module base() {
    difference() {
        union() {
            rounded_plate(plate_l, plate_w, plate_t, corner_r);
            pillar(1);
            pillar(-1);
            guide_tower();
            anchor_post();
        }
        // bench mounting holes
        for (x = [mount_hole_inset, plate_l - mount_hole_inset], y = [mount_hole_inset, plate_w - mount_hole_inset])
            translate([x, y, -fudge]) cylinder(d = m3_clear, h = plate_t + 2 * fudge);
        // window under the servo for its cable and airflow
        translate([servo_x - servo_w / 2 + 3, servo_y - servo_l / 2 + 4, -fudge])
            cube([servo_w - 6, servo_l - 8, plate_t + 2 * fudge]);
        ticks();
    }
}

module pulley_body() {   // use orientation: horn pocket down
    difference() {
        rotate_extrude() polygon([
            [0, 0], [r_rim, 0],
            [r_rim, pocket_depth + pulley_floor],
            [r_root, groove_z_in_pulley],                       // lower flank 45 deg
            [r_rim, groove_z_in_pulley + groove_depth],         // upper flank 45 deg
            [r_rim, pulley_h], [0, pulley_h]
        ]);
        translate([0, 0, -fudge]) cylinder(d = horn_d + 2 * tolerance, h = pocket_depth + fudge);   // centring pocket
        translate([0, 0, -fudge]) cylinder(d = horn_centre_screw_head_d + hole_comp + 0.3, h = pulley_h + 2 * fudge); // horn screw access
        for (i = [0 : horn_hole_n - 1]) rotate(i * 360 / horn_hole_n)
            translate([horn_hole_r, 0, -fudge]) {
                cylinder(d = horn_screw_d + hole_comp, h = pulley_h + 2 * fudge);
                translate([0, 0, pocket_depth + horn_screw_floor]) cylinder(d = horn_screw_head_d + hole_comp, h = pulley_h);
            }
    }
}

// Print orientation: flipped so the horn pocket opens UP (no 25mm flat ceiling to bridge).
// Tendon tie-off: radial hole from the groove root inward, then a vertical hole out the
// (printed) bottom face = the face that sits away from the horn in use.
tie_r = (horn_hole_r + r_root) / 2 + 0.5;
groove_z_print = pulley_h - groove_z_in_pulley;
module pulley() {
    difference() {
        translate([0, 0, pulley_h]) mirror([0, 0, 1]) pulley_body();
        rotate(180 / horn_hole_n) {
            translate([(tie_r + r_root + 1) / 2, 0, groove_z_print])
                teardrop_hole(tie_hole_d, r_root + 1 - tie_r, axis = "x");
            translate([tie_r, 0, -fudge]) cylinder(d = tie_hole_d, h = groove_z_print + fudge);
        }
    }
}

module servo_dummy() {   // assembly view only
    translate([servo_x - servo_w / 2, servo_y - servo_l / 2, servo_bottom_z]) cube([servo_w, servo_l, tab_bottom_h]);
    translate([servo_x - servo_w / 2, servo_y - (servo_l / 2 + tab_overhang), pillar_top_z + fudge]) cube([servo_w, servo_l + 2 * tab_overhang, tab_t]);
    translate([servo_x - servo_w / 2, servo_y - servo_l / 2, servo_bottom_z]) cube([servo_w, servo_l, servo_case_h]);
    translate([servo_x, shaft_y, servo_bottom_z + horn_top_h - horn_t]) cylinder(d = horn_d, h = horn_t);
}

module pulley_assembled() translate([servo_x, shaft_y, pulley_bottom_z + pulley_h]) mirror([0, 0, 1]) pulley();

// === ASSEMBLY / RENDER ===
part = "all"; // "all", "base", "pulley", "clash_pulley_base", "clash_servo_base"
if (part == "all") { base(); pulley_assembled(); %servo_dummy(); }
if (part == "base") base();
if (part == "pulley") pulley();
if (part == "clash_pulley_base") intersection() { base(); pulley_assembled(); }
if (part == "clash_servo_base") intersection() {
    base();
    translate([servo_x - servo_w / 2, servo_y - servo_l / 2, servo_bottom_z]) cube([servo_w, servo_l, tab_bottom_h - fudge]);
}
