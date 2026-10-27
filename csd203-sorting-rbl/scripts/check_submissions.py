"""Doi chieu SHA-256 cua ban goc va cac file da ghep vao du an."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_manifest(filename, field):
    manifest = ROOT / "ban_giao" / filename
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    errors = []
    for entry in entries:
        path = ROOT / entry[field]
        if not path.is_file():
            errors.append(entry[field] + ": missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            errors.append(entry[field] + ": changed")
    print(filename + ": " + str(len(entries) - len(errors)) + "/" + str(len(entries)) + " unchanged")
    for error in errors:
        print(error)
    return len(errors)


def main():
    errors = check_manifest("manifest.json", "original")
    errors += check_manifest("integrated.json", "active")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
