"""Pure geometry and tracking-loss tests; no camera, serial or ML packages."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pc"))
from camera import CHAINS, SAFE_POSE, joints_from_landmarks, next_targets


def straight_hand():
    points = [(0.0, 0.0, 0.0)] * 21
    for number, chain in enumerate(CHAINS.values()):
        direction = (0.2 * (number - 2), 1.0, 0.0)
        for distance, landmark in enumerate(chain, start=1):
            points[landmark] = tuple(x * distance for x in direction)
    return points


class CameraGeometryTests(unittest.TestCase):
    def test_straight_fingers_are_open(self):
        q = joints_from_landmarks(straight_hand())
        for joint in [0, 2, 3, 4, 5]:
            self.assertAlmostEqual(q[joint], 0.0, places=6)
        self.assertEqual(q[6], 0.5)

    def test_bending_index_closes_only_index_flexor(self):
        points = straight_hand()
        points[5] = (0.0, 1.0, 0.0)
        points[6] = (0.0, 2.0, 0.0)
        points[7] = (0.0, 2.0, 1.0)
        points[8] = (0.0, 1.0, 1.0)
        q = joints_from_landmarks(points)
        self.assertAlmostEqual(q[2], 0.75)
        for joint in [0, 3, 4, 5]:
            self.assertAlmostEqual(q[joint], 0.0, places=6)

    def test_rigid_transform_and_uniform_scale_invariant(self):
        original = straight_hand()
        original[7], original[8] = (0.0, 2.0, 1.0), (0.0, 1.0, 1.0)
        # 90-degree rotation around Z, scale to meters and translate.
        transformed = [(0.015 - 0.01 * y, -0.02 + 0.01 * x, 0.03 + 0.01 * z)
                       for x, y, z in original]
        for a, b in zip(joints_from_landmarks(original), joints_from_landmarks(transformed)):
            self.assertAlmostEqual(a, b, places=6)

    def test_tracking_loss_immediately_resets_target(self):
        previous = [1.0] * 7
        self.assertEqual(next_targets(previous, None), SAFE_POSE)
        self.assertEqual(previous, [1.0] * 7)
        self.assertEqual(next_targets(previous, [(0, 0, 0)] * 21), SAFE_POSE)

    def test_rejects_nan_or_wrong_shape(self):
        points = straight_hand()
        points[8] = (math.nan, 0, 0)
        with self.assertRaises(ValueError):
            joints_from_landmarks(points)
        with self.assertRaises(ValueError):
            joints_from_landmarks(points[:20])

    def test_output_is_bounded(self):
        for value in joints_from_landmarks(straight_hand()):
            self.assertTrue(math.isfinite(value) and 0 <= value <= 1)


if __name__ == "__main__":
    unittest.main()
