"""Package project sources and CAD, excluding environments, logs and model weights."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "output" / "robotic-hand-updated.zip"
    output.parent.mkdir(exist_ok=True)
    files = [root / "README.md", root / ".gitignore"]
    for directory in ("cad", "config", "docs", "firmware", "pc", "tests", "tools"):
        files.extend(p for p in (root / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts
                     and p.suffix not in (".pyc", ".wasm", ".o", ".exe"))
    model_readme = root / "models" / "README.md"
    if model_readme.is_file():
        files.append(model_readme)
    manifest = {}
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            relative = path.relative_to(root).as_posix()
            payload = path.read_bytes()
            manifest[relative] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
            archive.writestr("robotic-hand/" + relative, payload)
        archive.writestr("robotic-hand/MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        for name, details in manifest.items():
            payload = archive.read("robotic-hand/" + name)
            assert hashlib.sha256(payload).hexdigest() == details["sha256"]
    print(f"Verified {len(manifest)} files: {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
