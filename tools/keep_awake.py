"""Keep Windows awake until a completion flag appears, then optionally suspend.

Run in a dedicated process: the Windows execution-state request belongs to
the calling thread. Ctrl+C releases the request without putting the PC to sleep.
"""
import argparse
import ctypes
from pathlib import Path
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--done", type=Path, required=True)
    ap.add_argument("--sleep-on-completion", action="store_true")
    args = ap.parse_args()
    if args.done.exists():
        ap.error("Completion flag already exists; use a new flag path for this run")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.SetThreadExecutionState.argtypes = [ctypes.c_uint]
    kernel.SetThreadExecutionState.restype = ctypes.c_uint
    if not kernel.SetThreadExecutionState(0x80000001):
        raise ctypes.WinError(ctypes.get_last_error())
    print("Windows sleep prevented while work is active.", flush=True)
    completed = False
    try:
        while not args.done.exists():
            time.sleep(2)
        completed = True
        print("Work complete. Sleep requested in 45 seconds; Ctrl+C cancels.", flush=True)
        time.sleep(45)
    except KeyboardInterrupt:
        completed = False
        print("Sleep cancelled.", flush=True)
    finally:
        kernel.SetThreadExecutionState(0x80000000)
    if completed and args.sleep_on_completion:
        power = ctypes.WinDLL("powrprof", use_last_error=True)
        power.SetSuspendState.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]
        power.SetSuspendState.restype = ctypes.c_ubyte
        if not power.SetSuspendState(0, 0, 0):
            raise ctypes.WinError(ctypes.get_last_error())


if __name__ == "__main__":
    main()
