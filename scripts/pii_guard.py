#!/usr/bin/env python3
"""Fail if any real personal data is committed to the repository.

Scans every text file AND every cell inside .xlsx files, because the spreadsheet
is the most likely place for a real email to slip in.
"""
import os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
OK_EMAIL = re.compile(r"^(employee\d+|redacted\.\w+)@example\.invalid$")
PERSONAL_DOMAINS = ("gmail", "hotmail", "outlook", "yahoo", "icloud", "proton", "live", "zoho")
PHONE = re.compile(r"(?<!\d)(?:\+66|0)\d{1,2}[-\s]?\d{3}[-\s]?\d{4}(?!\d)")
SKIP_DIRS = {".git", "__pycache__", ".github"}
TEXT_EXT = (".md", ".json", ".csv", ".txt", ".yml", ".yaml", ".py", ".cfg", ".ini")

bad = []


def scan_text(name, text):
    for m in sorted(set(EMAIL.findall(text))):
        if OK_EMAIL.match(m):
            continue
        if m.lower().split("@")[-1].split(".")[0] in PERSONAL_DOMAINS:
            bad.append("%s: อีเมลส่วนบุคคล '%s'" % (name, m))
    for m in sorted(set(PHONE.findall(text))):
        bad.append("%s: เบอร์โทร '%s'" % (name, m))


for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        p = os.path.join(root, f)
        rel = os.path.relpath(p, ROOT)
        if f.endswith(".xlsx"):
            try:
                z = zipfile.ZipFile(p)
            except Exception:
                continue
            for n in z.namelist():
                if n.endswith((".xml", ".rels")):
                    scan_text("%s!%s" % (rel, n), z.read(n).decode("utf-8", "replace"))
        elif f.lower().endswith(TEXT_EXT):
            try:
                scan_text(rel, open(p, encoding="utf-8", errors="replace").read())
            except Exception:
                pass

if bad:
    print("พบข้อมูลส่วนบุคคล %d จุด — ห้าม commit:" % len(bad))
    for b in bad[:40]:
        print("  x " + b)
    sys.exit(1)
print("ไม่พบข้อมูลส่วนบุคคล ✓")
