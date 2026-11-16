"""Exercise serial boundary with a recorded in-memory transport."""
import csv
import json
from pathlib import Path
import queue
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pc"))
from hand import Hand
from control import ManualControl


class Transport:
    def __init__(self):
        self.input = queue.Queue()
        self.output = []
        self.closed = False

    def readline(self):
        try:
            return self.input.get(timeout=0.01)
        except queue.Empty:
            return b""

    def write(self, payload):
        self.output.append(json.loads(payload))

    def close(self):
        self.closed = True


class HandTests(unittest.TestCase):
    def setUp(self):
        self.transport = Transport()
        self.hand = Hand(transport=self.transport)
        self.addCleanup(self.hand.close)

    def test_bad_commands_never_reach_serial(self):
        for q in ([0] * 6, [0] * 8, [float("nan")] * 7,
                  [float("inf")] * 7, [True] * 7, ["0"] * 7):
            with self.subTest(q=q), self.assertRaises(ValueError):
                self.hand.send(q)
        self.assertEqual(self.transport.output, [])

    def test_clamp_preserves_channel_order(self):
        self.hand.send([-1, 0.1, 0.2, 0.3, 0.4, 0.5, 2])
        self.assertEqual(self.transport.output[-1],
                         {"t": "cmd", "q": [0, .1, .2, .3, .4, .5, 1]})

    def test_invalid_metadata_does_not_move_hardware(self):
        with self.assertRaises(ValueError):
            self.hand.send([0] * 7, extra={"force": float("nan")})
        self.assertEqual(self.transport.output, [])

    def test_reversed_calibration_and_invalid_limits(self):
        self.hand.calibrate(2, 120, 60)
        self.assertEqual(self.transport.output[-1],
                         {"t": "cal", "j": 2, "min": 120, "max": 60})
        for args in ((7, 60, 120), (True, 60, 120), (0, 90, 90),
                     (0, -1, 120), (0, 60, float("nan"))):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.hand.calibrate(*args)

    def test_reader_handles_whitespace_and_bad_rows(self):
        for line in (b"boot message\n", b"[]\n", b'{"t":"tel","q":[0]}\n',
                     b' { "q": [0,0,0,0,0,0,0.5], "t": "tel", "ms":42 }\n'):
            self.transport.input.put(line)
        deadline = time.monotonic() + 1
        while self.hand.telemetry is None and time.monotonic() < deadline:
            time.sleep(0.005)
        self.assertEqual(self.hand.telemetry["ms"], 42)

    def test_close_relaxes_once_and_joins_reader(self):
        self.hand.close()
        self.hand.close()
        self.assertEqual(self.transport.output, [{"t": "relax"}])
        self.assertTrue(self.transport.closed)
        self.assertFalse(self.hand._reader.is_alive())
        with self.assertRaises(RuntimeError):
            self.hand.send([0] * 7)

    def test_dry_logging_creates_folder_and_retains_empty_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "commands.csv"
            with Hand(dry=True, source="test", log_path=path) as hand:
                hand.send([0] * 7, extra={})
            with path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["source"], "test")
            self.assertEqual(json.loads(rows[0]["extra"]), {})

    def test_relax_remains_disabled_across_subsequent_gui_ticks(self):
        control = ManualControl(self.hand)
        control.send([0.5] * 7)
        self.assertEqual(self.transport.output, [])
        control.enable()
        control.send([0.5] * 7)
        control.relax()
        for _ in range(20):
            control.send([1] * 7)
        self.assertEqual([m["t"] for m in self.transport.output], ["cmd", "relax"])
        control.enable()
        control.send([0] * 7)
        self.assertEqual(self.transport.output[-1]["t"], "cmd")

    def test_calibration_does_not_reenable_motion(self):
        control = ManualControl(self.hand)
        control.enable()
        control.calibrate(0, 120, 60)
        control.send([1] * 7)
        self.assertFalse(control.enabled)
        self.assertEqual([m["t"] for m in self.transport.output], ["relax", "cal"])


if __name__ == "__main__":
    unittest.main()
