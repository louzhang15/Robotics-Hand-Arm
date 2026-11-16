"""Hardware-independent tests of the actual C++ state machine via WebAssembly."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FirmwareCoreTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("clang++") and shutil.which("node"),
                         "Firmware core host tests require clang++ (wasm32) and Node.js")
    def test_actual_cpp_state_machine(self):
        output = ROOT / "build" / "firmware-tests" / "executor.wasm"
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "clang++", "--target=wasm32", "-O2", "-nostdlib",
            "-Wl,--no-entry", "-Wl,--export-all", "-o", str(output),
            str(ROOT / "tests" / "firmware_core.cpp"),
        ], check=True, cwd=ROOT, capture_output=True, text=True)
        subprocess.run(["node", str(ROOT / "tests" / "firmware_core.test.cjs"),
                        str(output)], check=True, cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
