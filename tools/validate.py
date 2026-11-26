#!/usr/bin/env python3
"""Перевірка ресурсів теми: XML на валідність, PNG на сигнатуру та розміри."""

import glob
import os
import struct
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPECTED_SIZES = {
    "drawable-mdpi": 48,
    "drawable-hdpi": 72,
    "drawable-xhdpi": 96,
    "drawable-xxhdpi": 144,
    "drawable-xxxhdpi": 192,
}


def main():
    errors = []

    xml_files = glob.glob(os.path.join(ROOT, "app", "src", "main", "**", "*.xml"), recursive=True)
    for f in xml_files:
        try:
            ET.parse(f)
            print("XML OK:", os.path.relpath(f, ROOT))
        except ET.ParseError as e:
            errors.append("XML FAIL: %s: %s" % (f, e))

    for folder, size in EXPECTED_SIZES.items():
        pattern = os.path.join(ROOT, "app", "src", "main", "res", folder, "*.png")
        for f in glob.glob(pattern):
            rel = os.path.relpath(f, ROOT)
            with open(f, "rb") as fh:
                data = fh.read(33)
            if data[:8] != b"\x89PNG\r\n\x1a\n":
                errors.append("PNG FAIL (signature): %s" % rel)
                continue
            w, h = struct.unpack(">II", data[16:24])
            if w != size or h != size:
                errors.append("PNG FAIL (size %dx%d, expected %d): %s" % (w, h, size, rel))
            else:
                print("PNG OK:", rel, "%dx%d" % (w, h))

    gen = os.path.join(ROOT, "tools", "generate_icons.py")
    with open(gen, "r", encoding="utf-8") as fh:
        compile(fh.read(), gen, "exec")
    print("PY OK: tools/generate_icons.py")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
