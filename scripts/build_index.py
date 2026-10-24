#!/usr/bin/env python3
"""Rebuild app/index.json from the table files and check that it is current."""
import json, os, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, "app", "index.json")
index = json.load(open(IDX, encoding="utf-8"))

missing = [t["file"] for t in index["tables"] if not os.path.exists(os.path.join(ROOT, t["file"]))]
if missing:
    print("ไฟล์ตารางหายไป %d ไฟล์:" % len(missing))
    for m in missing[:10]:
        print("   ", m)
    sys.exit(1)

changed = []
for t in index["tables"]:
    obj = json.load(open(os.path.join(ROOT, t["file"]), encoding="utf-8"))
    if obj.get("table") != t["name"]:
        changed.append(t["file"])
print("ตาราง %d ตาราง · ข้อมูลตรงกับ index: %s"
      % (len(index["tables"]), "ok" if not changed else "MISMATCH %s" % changed[:3]))
sys.exit(1 if changed or missing else 0)
