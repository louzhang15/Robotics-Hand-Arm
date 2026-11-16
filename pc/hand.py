"""Serial boundary for input apps. Telemetry q is commanded, not measured."""
import csv
import json
import math
from pathlib import Path
import threading
import time

JOINTS = ["thumb_flex", "thumb_opp", "index", "middle", "ring", "pinky", "wrist"]


def joint_vector(q):
    values = list(q)
    if len(values) != 7:
        raise ValueError("Exactly 7 joint values are required")
    if any(isinstance(v, (bool, str, bytes)) for v in values):
        raise ValueError("Joint values must be finite numbers")
    values = [float(v) for v in values]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Joint values must be finite numbers")
    return [round(min(1.0, max(0.0, v)), 3) for v in values]


class Hand:
    JOINTS = JOINTS

    def __init__(self, port="COM5", baud=115200, log_path=None,
                 source="unknown", *, dry=False, transport=None):
        self.telemetry = None
        self.source = source
        self._closed = False
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._log = None
        self._reader = None
        self.ser = transport
        if self.ser is None and not dry:
            import serial
            self.ser = serial.Serial(port, baud, timeout=0.1, write_timeout=0.5)
        try:
            if log_path:
                path = Path(log_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                f = path.open("a", newline="", encoding="utf-8")
                self._log = (f, csv.writer(f))
                if f.tell() == 0:
                    self._log[1].writerow(["t", "source"] + [f"q_{j}" for j in JOINTS]
                                         + ["telemetry", "extra"])
            if self.ser:
                self._reader = threading.Thread(target=self._read, daemon=True)
                self._reader.start()
        except Exception:
            if self.ser:
                self.ser.close()
            raise

    def _write(self, message):
        if self._closed:
            raise RuntimeError("Hand is closed")
        payload = (json.dumps(message, allow_nan=False) + "\n").encode()
        with self._lock:
            if self.ser:
                self.ser.write(payload)

    def send(self, q, extra=None):
        q = joint_vector(q)
        metadata = json.dumps(extra, allow_nan=False) if extra is not None else ""
        self._write({"t": "cmd", "q": q})
        if self._log:
            self._log[1].writerow([f"{time.time():.6f}", self.source] + q +
                                  [json.dumps(self.telemetry), metadata])
            self._log[0].flush()

    def calibrate(self, joint, lo, hi):
        if isinstance(joint, bool) or not isinstance(joint, int) or not 0 <= joint < 7:
            raise ValueError("Joint index must be 0..6")
        if any(isinstance(v, (bool, str)) for v in (lo, hi)):
            raise ValueError("Calibration endpoints must be numbers")
        lo, hi = float(lo), float(hi)
        if not all(math.isfinite(v) and 0 <= v <= 180 for v in (lo, hi)) or lo == hi:
            raise ValueError("Distinct endpoints must lie in 0..180 degrees")
        self._write({"t": "cal", "j": joint, "min": lo, "max": hi})

    def relax(self):
        self._write({"t": "relax"})

    def close(self):
        if self._closed:
            return
        try:
            self.relax()
        finally:
            self._closed = True
            self._stop.set()
            if self._reader:
                self._reader.join(timeout=1)
            if self.ser:
                self.ser.close()
            if self._log:
                self._log[0].close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _read(self):
        while not self._stop.is_set():
            try:
                line = self.ser.readline()
            except (OSError, ValueError):
                return
            try:
                message = json.loads(line)
                if isinstance(message, dict) and message.get("t") == "tel":
                    q = message.get("q")
                    if isinstance(q, list) and len(q) == 7:
                        joint_vector(q)
                        self.telemetry = message
            except (ValueError, TypeError, OverflowError):
                continue
