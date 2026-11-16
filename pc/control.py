"""Manual motion gate, independent of the GUI event loop."""


class ManualControl:
    def __init__(self, hand):
        self.hand = hand
        self.enabled = False

    def enable(self):
        self.enabled = True

    def relax(self):
        # Disable first, including when the serial write fails.
        self.enabled = False
        self.hand.relax()

    def send(self, targets):
        if self.enabled:
            self.hand.send(targets)

    def calibrate(self, joint, lo, hi):
        self.relax()
        self.hand.calibrate(joint, lo, hi)
