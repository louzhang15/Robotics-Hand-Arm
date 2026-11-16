"""Read Bambu project presets without starting the slicer or a print."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths or sorted((Path(__file__).resolve().parents[1] / "cad").glob("*.3mf"))
    for path in paths:
        print(path.name)
        with ZipFile(path) as archive:
            name = "Metadata/project_settings.config"
            if name not in archive.namelist():
                print("  No Bambu project preset; select printer/material in slicer.")
                continue
            settings = json.loads(archive.read(name))
        for key in ("printer_settings_id", "filament_settings_id", "layer_height",
                    "wall_loops", "sparse_infill_density", "enable_support"):
            print(f"  {key}: {settings.get(key, 'not embedded')}")
        filaments = settings.get("filament_settings_id", [])
        if any("PLA" in item.upper() for item in filaments):
            print("  WARNING: PLA preset embedded; the structural build plan calls for PETG.")
        print("  Preset metadata does not verify slicing, material fit or structural strength.")


if __name__ == "__main__":
    main()
