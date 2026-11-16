// Robotic Hand: seven removable servo cartridges on an open chassis.
// CONCEPT ONLY. Default MG996R dimensions are unmeasured assumptions.
// Units mm. X elbow -> hand, Y transverse, Z shaft-up.
// No finger model, load rating, final tendon routing, or arm bearing is claimed.
part = "assembly"; // chassis, cartridge, adapter, assembly
$fn = $preview ? 32 : 64;
eps = 0.02;
chassis_l = 248;
chassis_w = 156;
chassis_t = 5;
cartridge_l = 42;
cartridge_w = 66;
cartridge_t = 5;
servo_l = 40.7; // along Y; verify every purchased servo
servo_w = 19.7;
servo_case_h = 42.9;
tab_bottom_h = 26.6;
tab_hole_spacing_l = 49.5;
tab_hole_spacing_w = 10;
insert_hole_d = 4.0; // M3 inserts: measure manufacturer recommendation
insert_len = 5.7;
case_floor_gap = 1;
fit_gap = 0.4;
clearance_d = 3.6;
shaft_offset_y = servo_l/2 - 10.2;
horn_above_case = 4;
pulley_radius = 17;
pulley_h = 12.5;
cable_bore_d = 20; // >=15 mm, normal to chassis; elbow adapter remains replaceable
adapter_l = 38;
adapter_w = 60;
adapter_t = 6;
adapter_x = 20;
adapter_y = chassis_w/2;
// Paired banks carry flexors/opposition; seventh cartridge reserves wrist actuator.
// These positions do NOT specify tendon routing or final joint mapping.
positions = [[62,37],[62,119],[114,37],[114,119],
             [166,37],[166,119],[218,78]];
case_bottom_z = cartridge_t + case_floor_gap;
pillar_top = case_bottom_z + tab_bottom_h;
pillar_inner_y = servo_l/2 + fit_gap;
pillar_depth = 10;
assert(chassis_l <= 256 && chassis_w <= 256, "Chassis exceeds nominal A1 plate");
assert(cable_bore_d >= 15, "Cable passage must be at least 15 mm");
assert(cartridge_l > servo_w + 2*fit_gap + 8, "Cartridge has insufficient side rail");
assert(tab_hole_spacing_l/2 - pillar_inner_y - insert_hole_d/2 >= 1.6,
       "Insert too near inner pillar face; change measured mount geometry");
assert(insert_len + 2 < pillar_top-cartridge_t, "Insert too deep");
assert(adapter_l/2 - 12 - clearance_d/2 >= 3, "Adapter edge too thin");
for (p = positions) {
    assert(p[0]-cartridge_l/2 > 0 && p[0]+cartridge_l/2 < chassis_l, "Cartridge outside X boundary");
    assert(p[1]-cartridge_w/2 > 0 && p[1]+cartridge_w/2 < chassis_w, "Cartridge outside Y boundary");
}

module corner_bores(height) {
    for (x=[5,cartridge_l-5], y=[4,cartridge_w-4])
        translate([x,y,-eps]) cylinder(d=clearance_d,h=height+2*eps);
}
module adapter_bores(height) {
    for (x=[-12,12],y=[-22,22]) translate([x,y,-eps])
        cylinder(d=clearance_d,h=height+2*eps);
    translate([0,0,-eps]) cylinder(d=cable_bore_d,h=height+2*eps);
}
module cartridge() {
    difference() {
        union() {
            cube([cartridge_l,cartridge_w,cartridge_t]);
            // Tabs seat on two pillars. Case is not used as a load-bearing stop.
            for(s=[-1,1])
                translate([cartridge_l/2-11,cartridge_w/2+s*(pillar_inner_y+pillar_depth/2)-pillar_depth/2,cartridge_t-eps])
                    cube([22,pillar_depth,pillar_top-cartridge_t+eps]);
        }
        // Access window below hanging case. A fit_gap-wide ledge at either Y
        // end avoids a coplanar cut coincident with the inner pillar face.
        // Case bottom remains case_floor_gap above the base, so it clears.
        translate([cartridge_l/2-servo_w/2-fit_gap,cartridge_w/2-servo_l/2,-eps])
            cube([servo_w+2*fit_gap,servo_l,pillar_top+2*eps]);
        corner_bores(cartridge_t);
        for(s=[-1,1], dx=[-1,1])
            translate([cartridge_l/2+dx*tab_hole_spacing_w/2,
                       cartridge_w/2+s*tab_hole_spacing_l/2,pillar_top-insert_len])
                cylinder(d=insert_hole_d,h=insert_len+eps);
        // Cable exit slots through the pillar floor, not through the insert zone.
        for(s=[-1,1])
            translate([cartridge_l/2-5,cartridge_w/2+s*(pillar_inner_y+pillar_depth/2)-pillar_depth/2-eps,cartridge_t-eps])
                cube([10,pillar_depth+2*eps,7]);
    }
}
module chassis() {
    difference() {
        cube([chassis_l,chassis_w,chassis_t]);
        for(p=positions) {
            // Cartridges bolt through chassis; cavity allows wiring access below.
            translate([p[0]-cartridge_l/2,p[1]-cartridge_w/2,0]) corner_bores(chassis_t);
            translate([p[0]-13,p[1]-22,-eps]) cube([26,44,chassis_t+2*eps]);
        }
        translate([adapter_x,adapter_y,0]) adapter_bores(chassis_t);
        // Additional strain-relief tie slots on each long edge.
        for(x=[40,92,144,196],y=[8,chassis_w-8])
            translate([x-4,y-1.5,-eps]) cube([8,3,chassis_t+2*eps]);
    }
}
module adapter() {
    // Flat service interface. Future elbow clevis/roll unit replaces this plate.
    difference() {
        translate([-adapter_l/2,-adapter_w/2,0]) cube([adapter_l,adapter_w,adapter_t]);
        adapter_bores(adapter_t);
    }
}
module servo_envelope() {
    color([0.1,0.15,0.2,0.65])
        translate([cartridge_l/2-servo_w/2,cartridge_w/2-servo_l/2,case_bottom_z])
            cube([servo_w,servo_l,servo_case_h]);
    color([0.2,0.2,0.2,0.65])
        translate([cartridge_l/2-servo_w/2,cartridge_w/2-tab_hole_spacing_l/2-3,pillar_top])
            cube([servo_w,tab_hole_spacing_l+6,2.5]);
    color([0.95,0.7,0.15,0.8])
        translate([cartridge_l/2,cartridge_w/2+shaft_offset_y,case_bottom_z+servo_case_h+horn_above_case])
            cylinder(r=pulley_radius,h=pulley_h);
}
module assembly() {
    color([0.65,0.7,0.75]) chassis();
    for(p=positions) translate([p[0]-cartridge_l/2,p[1]-cartridge_w/2,chassis_t]) {
        color([0.15,0.5,0.7]) cartridge();
        servo_envelope();
    }
    color([0.9,0.4,0.18]) translate([adapter_x,adapter_y,chassis_t]) adapter();
}
if(part=="chassis") chassis();
else if(part=="cartridge") cartridge();
else if(part=="adapter") translate([adapter_l/2,adapter_w/2,0]) adapter();
else if(part=="assembly") assembly();
else assert(false,"Unknown part");
echo(status="CONCEPT - UNMEASURED", chassis=[chassis_l,chassis_w,chassis_t],
     cartridge=[cartridge_l,cartridge_w,pillar_top], cable_bore=cable_bore_d);
