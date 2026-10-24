#!/usr/bin/env python3
"""Validate submitted findings and guard against PII leaking into the repo.

Usage:
    python3 scripts/validate_findings.py analysis/findings/<file>.json [...]

Exit code 0 = ok, 1 = errors found.

Checks
  1. JSON parses, required structure present
  2. required fields of every finding
  3. vocabulary: verdict / severity / domain / property / confidence
  4. the referenced table really exists in the app (app/index.json)
  5. no duplicate id inside the file, and no id already used by another file
  6. no PII: real email addresses, phone numbers
"""
import json, os, re, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = json.load(open(os.path.join(ROOT, "schema", "finding.schema.json"), encoding="utf-8"))
INDEX = json.load(open(os.path.join(ROOT, "app", "index.json"), encoding="utf-8"))

PROPS = SCHEMA["$defs"]["finding"]["properties"]
VERDICTS = set(PROPS["verdict"]["enum"])
SEVERITIES = set(PROPS["severity"]["enum"])
PROPERTIES = set(PROPS["property"]["enum"])
CONFIDENCE = set(PROPS["confidence"]["enum"])
REQUIRED = SCHEMA["$defs"]["finding"]["required"]
DOMAINS = {d["code"] for d in INDEX["domains"]}

TABLES = {t["name"] for t in INDEX["tables"]}
COLUMNS = {}
for t in INDEX["tables"]:
    try:
        obj = json.load(open(os.path.join(ROOT, t["file"]), encoding="utf-8"))
    except Exception:
        continue
    names = {c["name"] for c in obj.get("columns", [])}
    names |= {a["name"] for a in obj.get("actions", [])}
    COLUMNS[t["name"]] = names

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
OK_EMAIL = re.compile(r"^(employee\d+|redacted\.\w+)@example\.invalid$")
PHONE_RE = re.compile(r"(?<!\d)(?:\+66|0)\d{1,2}[-\s]?\d{3}[-\s]?\d{4}(?!\d)")

errors, warnings = [], []


def err(f, msg):
    errors.append("%s: %s" % (f, msg))


def warn(f, msg):
    warnings.append("%s: %s" % (f, msg))


def check_pii(fname, text):
    for m in sorted(set(EMAIL_RE.findall(text))):
        if not OK_EMAIL.match(m):
            err(fname, "พบอีเมลจริง '%s' — ต้องลบหรือแทนด้วย employeeNN@example.invalid" % m)
    for m in sorted(set(PHONE_RE.findall(text))):
        err(fname, "พบเบอร์โทร '%s' — ข้อมูลส่วนบุคคลต้องไม่อยู่ใน repo" % m)


def validate_file(path):
    rel = os.path.relpath(path, ROOT)
    raw = open(path, encoding="utf-8").read()
    check_pii(rel, raw)
    try:
        doc = json.loads(raw)
    except Exception as e:
        err(rel, "JSON parse ไม่ผ่าน: %s" % e)
        return set()
    if not isinstance(doc, dict) or "meta" not in doc or "findings" not in doc:
        err(rel, "ต้องมีคีย์ 'meta' และ 'findings'")
        return set()
    meta = doc["meta"]
    if not isinstance(meta, dict):
        err(rel, "meta ต้องเป็น object")
    else:
        for k in ("agent", "task", "created_at"):
            if not meta.get(k):
                err(rel, "meta.%s ว่าง" % k)
    fl = doc["findings"]
    if not isinstance(fl, list):
        err(rel, "findings ต้องเป็น list")
        return set()
    ids = set()
    for i, f in enumerate(fl):
        tag = "%s findings[%d]" % (rel, i)
        if not isinstance(f, dict):
            err(tag, "ไม่ใช่ object")
            continue
        for k in REQUIRED:
            if not f.get(k):
                err(tag, "ขาดฟิลด์ '%s'" % k)
        fid = f.get("id", "")
        if fid:
            if fid in ids:
                err(tag, "id ซ้ำในไฟล์เดียวกัน: %s" % fid)
            ids.add(fid)
        for key, allowed in (("verdict", VERDICTS), ("severity", SEVERITIES),
                             ("confidence", CONFIDENCE), ("property", PROPERTIES)):
            v = f.get(key)
            if v and v not in allowed:
                err(tag, "%s '%s' ไม่อยู่ในคำศัพท์ที่อนุญาต" % (key, v))
        if f.get("domain") and f["domain"] not in DOMAINS:
            err(tag, "domain '%s' ไม่มีในแอป" % f["domain"])
        src = f.get("source")
        if not isinstance(src, dict):
            err(tag, "source ต้องเป็น object ที่มี pdf_page")
        else:
            pg = src.get("pdf_page")
            if not isinstance(pg, int) or not (1 <= pg <= 1946):
                err(tag, "source.pdf_page ต้องเป็นเลขหน้า 1-1946")
        t = f.get("table")
        if t and t not in TABLES and t != "(หลายตาราง)":
            err(tag, "ไม่พบตาราง '%s' ใน app/index.json" % t)
        c = f.get("column")
        if t in COLUMNS and c and c not in COLUMNS[t] and not str(c).startswith("("):
            warn(tag, "ไม่พบคอลัมน์ '%s' ในตาราง '%s' (ตรวจชื่ออีกครั้ง)" % (c, t))
        if f.get("verdict") == "ต้องยืนยันในแอป" and f.get("severity") in ("critical", "high"):
            warn(tag, "verdict 'ต้องยืนยันในแอป' ไม่ควรมี severity สูงเกิน low")
        if len(str(f.get("falsifiable_test", ""))) < 10:
            err(tag, "ต้องมี falsifiable_test ที่ชัดเจน")
    return ids


def main():
    files = sys.argv[1:]
    if not files:
        files = sorted(glob.glob(os.path.join(ROOT, "analysis", "findings", "*.json")))
    if not files:
        print("ไม่มีไฟล์ findings ให้ตรวจ")
        return 0

    seen = {}
    for p in files:
        rel = os.path.relpath(p, ROOT)
        try:
            doc = json.loads(open(p, encoding="utf-8").read())
        except Exception:
            continue
        for f in doc.get("findings", []) or []:
            if isinstance(f, dict) and f.get("id"):
                seen.setdefault(f["id"], []).append(rel)

    all_ids = set()
    for p in files:
        ids = validate_file(p)
        for i in ids:
            if len(seen.get(i, [])) > 1:
                err(os.path.relpath(p, ROOT),
                    "id ซ้ำกับไฟล์อื่น: %s (%s)" % (i, ", ".join(seen[i])))
        all_ids |= ids

    base_path = os.path.join(ROOT, "analysis", "findings", "000-baseline-quality.json")
    if os.path.exists(base_path):
        base = json.load(open(base_path, encoding="utf-8"))
        base_ids = {f.get("id") for f in base.get("findings", [])}
        dup = (base_ids & all_ids) - base_ids if False else set()
        # only compare the baseline against the OTHER files
        others = set()
        for p in files:
            if os.path.abspath(p) == os.path.abspath(base_path):
                continue
            try:
                d = json.loads(open(p, encoding="utf-8").read())
            except Exception:
                continue
            for f in d.get("findings", []) or []:
                if isinstance(f, dict) and f.get("id"):
                    others.add(f["id"])
        dup = base_ids & others
        if dup:
            warn("baseline", "id ซ้ำกับ baseline %d รายการ (เช่น %s) — ถ้าเป็นของเดิมให้ขยาย baseline แทนที่จะเพิ่มใหม่"
                 % (len(dup), sorted(dup)[0]))

    print("ตรวจ %d ไฟล์ · %d finding" % (len(files), len(all_ids)))
    if warnings:
        print("\nคำเตือน %d รายการ:" % len(warnings))
        for w in warnings:
            print("  ! " + w)
    if errors:
        print("\nผิดพลาด %d รายการ:" % len(errors))
        for e in errors:
            print("  x " + e)
        return 1
    print("\nผ่านทั้งหมด ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
