"""Webcam mirroring through MediaPipe Tasks (optional camera dependencies).

python pc/camera.py --model models/hand_landmarker.task --dry
python pc/camera.py --model models/hand_landmarker.task --port COM5 --log runs/camera.csv

Download the Hand Landmarker task model linked from Google's official guide:
https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
This program never downloads code or model files automatically. --dry never opens
serial hardware. Lost tracking commands open fingers and neutral wrist; a stalled
process relies on the executor watchdog. Thresholds require per-user calibration.
"""
import argparse
import math
from pathlib import Path
import time

CHAINS = {"thumb_flex": (1, 2, 3, 4), "index": (5, 6, 7, 8),
          "middle": (9, 10, 11, 12), "ring": (13, 14, 15, 16),
          "pinky": (17, 18, 19, 20)}
MAX_BEND = {"thumb_flex": 120, "index": 240, "middle": 240,
            "ring": 240, "pinky": 240}
OPP_FAR, OPP_NEAR = 1.1, 0.45
SAFE_POSE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5]
CONNECTIONS = [(0, 1), (0, 5), (0, 17), (5, 9), (9, 13), (13, 17)] + [
    pair for chain in CHAINS.values() for pair in zip(chain, chain[1:])]


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _norm(v):
    return math.sqrt(sum(x * x for x in v))


def angle(a, b):
    denominator = _norm(a) * _norm(b)
    if denominator < 1e-16:
        raise ValueError("Degenerate landmark segment")
    cosine = sum(x * y for x, y in zip(a, b)) / denominator
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def joints_from_landmarks(landmarks):
    """Map 21 world-space points (meters) to 7 targets, without I/O.

    World landmarks avoid image aspect-ratio distortion in normalized x/y.
    Opposition is a provisional distance heuristic, not a measured joint angle.
    """
    p = [tuple(float(v) for v in ((l.x, l.y, l.z) if hasattr(l, "x") else l))
         for l in landmarks]
    if len(p) != 21 or any(len(v) != 3 for v in p):
        raise ValueError("Expected 21 three-dimensional landmarks")
    if not all(math.isfinite(v) for point in p for v in point):
        raise ValueError("Landmarks must be finite")
    curl = {}
    for name, (a, b, c, d) in CHAINS.items():
        segments = [_sub(p[a], p[0]), _sub(p[b], p[a]),
                    _sub(p[c], p[b]), _sub(p[d], p[c])]
        bend = sum(angle(segments[i], segments[i + 1]) for i in range(3))
        curl[name] = min(1.0, bend / MAX_BEND[name])
    palm = _norm(_sub(p[9], p[0]))
    if palm < 1e-8:
        raise ValueError("Degenerate palm")
    distance = _norm(_sub(p[4], p[17])) / palm
    opposition = max(0.0, min(1.0, (OPP_FAR - distance) / (OPP_FAR - OPP_NEAR)))
    return [curl["thumb_flex"], opposition, curl["index"], curl["middle"],
            curl["ring"], curl["pinky"], 0.5]


def next_targets(previous, landmarks):
    """Reset immediately on missing/invalid tracking; firmware rate-limits motion."""
    if landmarks is None:
        return SAFE_POSE.copy()
    try:
        target = joints_from_landmarks(landmarks)
    except (ValueError, TypeError, AttributeError, OverflowError):
        return SAFE_POSE.copy()
    return [0.6 * old + 0.4 * new for old, new in zip(previous, target)]


def draw_landmarks(cv2, frame, landmarks):
    height, width = frame.shape[:2]
    points = [(int(l.x * width), int(l.y * height)) for l in landmarks]
    for a, b in CONNECTIONS:
        cv2.line(frame, points[a], points[b], (80, 220, 80), 2)
    for point in points:
        cv2.circle(frame, point, 3, (30, 120, 255), -1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", default="COM5")
    ap.add_argument("--cam", type=int, default=0)
    ap.add_argument("--model", required=True, type=Path,
                    help="Local Hand Landmarker .task model from Google's model download")
    ap.add_argument("--log")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args(argv)
    if not args.model.is_file():
        ap.error(f"Model file does not exist: {args.model}")
    try:
        import cv2
        import mediapipe as mp
    except ImportError as exc:
        ap.error(f"Install camera dependencies: pip install -r pc/requirements-camera.txt ({exc})")
    from hand import Hand

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(args.model.resolve())),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1, min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6, min_tracking_confidence=0.6)
    cap = None
    try:
        # Create the model and camera before opening the serial device.
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as tracker:
            cap = cv2.VideoCapture(args.cam)
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open camera {args.cam}")
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # backend may ignore this hint
            with Hand(args.port, log_path=args.log, source="camera", dry=args.dry) as hand:
                smooth = SAFE_POSE.copy()
                last_send = float("-inf")
                last_timestamp = -1
                while cap.isOpened():
                    # No more than 20 commands/s, including fast prerecorded backends.
                    time.sleep(max(0.0, 0.05 - (time.monotonic() - last_send)))
                    ok, frame = cap.read()
                    if not ok:
                        break
                    timestamp = max(last_timestamp + 1, time.monotonic_ns() // 1_000_000)
                    last_timestamp = timestamp
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = tracker.detect_for_video(
                        mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
                    world = result.hand_world_landmarks[0] if result.hand_world_landmarks else None
                    tracked = world is not None
                    if tracked:
                        try:
                            joints_from_landmarks(world)
                        except (ValueError, TypeError, AttributeError, OverflowError):
                            tracked = False
                    smooth = next_targets(smooth, world if tracked else None)
                    hand.send(smooth, extra={"tracked": tracked, "frame_ms": timestamp})
                    last_send = time.monotonic()
                    if args.dry:
                        print(" ".join(f"{v:.3f}" for v in smooth))
                    if result.hand_landmarks:
                        draw_landmarks(cv2, frame, result.hand_landmarks[0])
                    label = "Tracking" if tracked else "No valid hand: opening fingers"
                    cv2.putText(frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 200, 255), 2)
                    cv2.imshow("Hand camera (Esc quits)", frame)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
