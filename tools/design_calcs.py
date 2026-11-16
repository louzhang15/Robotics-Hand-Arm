"""Planning calculations only; no continuous-load or physical fit certification."""
import argparse
import json
import math
from pathlib import Path


def pulley_radius_mm(travel_mm, rotation_deg):
    if not (math.isfinite(travel_mm) and math.isfinite(rotation_deg)
            and travel_mm > 0 and 0 < rotation_deg <= 360):
        raise ValueError("Positive travel and rotation in (0, 360] required")
    return travel_mm / math.radians(rotation_deg)


def gravity_torque_nm(mass_kg, lever_m):
    if not all(math.isfinite(v) and v >= 0 for v in (mass_kg, lever_m)):
        raise ValueError("Mass and lever arm must be finite and nonnegative")
    return mass_kg * 9.80665 * lever_m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config/measurements.json")
    args = ap.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    default = config["planning_defaults"]
    measured_travel = config["tendon"]["finger_full_curl_pull_mm"]
    measured_angle = config["servo"]["usable_rotation_deg"]
    travel = default["tendon_pull_mm"] if measured_travel is None else measured_travel
    angle = default["servo_rotation_deg"] if measured_angle is None else measured_angle
    radius = pulley_radius_mm(travel, angle)
    force = default["servo_stall_torque_kgf_cm"] * 0.0980665 / (radius / 1000)
    current = default["servo_count"] * default["servo_stall_current_a"]
    print("PLANNING ESTIMATES - use measured values before fabricating")
    print(f"Tendon pull {travel:g} mm / usable travel {angle:g} deg -> radius {radius:.2f} mm")
    print(f"Ideal stall tendon force: {force:.1f} N (NOT a continuous operating load)")
    print(f"Servo-only mass: {default['servo_count'] * default['servo_mass_g']} g")
    print(f"Nominal simultaneous stall current: {current:.1f} A")
    print(f"Supply spare at that estimate: {default['supply_current_a'] - current:.1f} A; clones/transients may exceed estimate")
    assembly = config["assembly"]
    if all(v is not None for v in assembly.values()):
        torque = gravity_torque_nm(assembly["hand_forearm_mass_kg"], assembly["hand_forearm_center_of_mass_m"])
        print(f"Assembly static moment: {torque:.2f} Nm; 2x {torque * 2:.2f} Nm")
        print("Add payload, arm link masses, acceleration and drivetrain losses separately.")
    else:
        print("Arm torque sizing pending measured masses and centers of mass.")


if __name__ == "__main__":
    main()
