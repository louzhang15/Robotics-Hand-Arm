"""20 Hz manual control; starts disabled. python pc/sliders.py --dry"""
import argparse
import tkinter as tk
from tkinter import messagebox
from hand import Hand
from control import ManualControl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM5")
    ap.add_argument("--log")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    hand = Hand(args.port, log_path=args.log, source="sliders", dry=args.dry)
    root = tk.Tk()
    root.title("Hand control" + (" (simulation)" if args.dry else ""))
    control = ManualControl(hand)
    values = []
    for i, name in enumerate(Hand.JOINTS):
        row = tk.Frame(root)
        row.pack(fill="x")
        v = tk.DoubleVar(value=0.5 if i == 6 else 0)
        tk.Scale(row, label=name, from_=0, to=1, resolution=0.01,
                 orient="horizontal", length=320, variable=v).pack(side="left")
        lo, hi = tk.DoubleVar(value=60), tk.DoubleVar(value=120)
        tk.Spinbox(row, from_=0, to=180, width=5, textvariable=lo).pack(side="left")
        tk.Spinbox(row, from_=0, to=180, width=5, textvariable=hi).pack(side="left")

        def calibrate(j=i, lo=lo, hi=hi):
            try:
                control.relax()
                control.calibrate(j, lo.get(), hi.get())
            except (OSError, ValueError, tk.TclError) as exc:
                messagebox.showerror("Calibration", str(exc))
        tk.Button(row, text="Cal (RAM)", command=calibrate).pack(side="left")
        values.append(v)

    def relax():
        try:
            control.relax()
        except OSError as exc:
            messagebox.showerror("Serial connection", str(exc))

    tk.Button(root, text="Enable motion at current sliders", command=control.enable).pack(fill="x")
    tk.Button(root, text="Relax / disable motion", command=relax).pack(fill="x")
    status = tk.Label(root)
    status.pack()

    def tick():
        if control.enabled:
            try:
                control.send([v.get() for v in values])
            except (OSError, ValueError) as exc:
                control.enabled = False
                messagebox.showerror("Motion stopped", str(exc))
        status.config(text=("Enabled" if control.enabled else "Disabled") +
                      " | telemetry q is commanded position")
        root.after(50, tick)

    def close():
        control.enabled = False
        try:
            hand.close()
        finally:
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    tick()
    root.mainloop()


if __name__ == "__main__":
    main()
