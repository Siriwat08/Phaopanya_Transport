#!/usr/bin/env python3
"""Scaffold a new findings file that satisfies the contract.

    python3 scripts/new_finding.py <agent-name> <task-id>
"""
import json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent, task = (sys.argv[1] if len(sys.argv) > 1 else "your-agent"), \
              (sys.argv[2] if len(sys.argv) > 2 else "00-example")
out = os.path.join(ROOT, "findings", "%s-%s.json" % (agent, task))
doc = {
    "meta": {
        "agent": agent,
        "task": task,
        "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "pdf_available": False,
        "notes": ""
    },
    "findings": [
        {
            "id": "D00|ตาราง|คอลัมน์|App formula|example-001",
            "table": "ชื่อตาราง",
            "column": "ชื่อคอลัมน์",
            "property": "App formula",
            "domain": "D01",
            "verdict": "พอใช้",
            "severity": "low",
            "problem": "อธิบายปัญหาให้ชัดใน 1-2 บรรทัด",
            "evidence": "ยกสูตร/ค่าจริงที่เป็นหลักฐาน",
            "impact": "ผลต่อธุรกิจ",
            "recommendation": "วิธีแก้",
            "suggested_formula": "",
            "source": {"pdf_page": 1, "property": "App formula"},
            "falsifiable_test": "อะไรจะพิสูจน์ว่าข้อนี้ผิด",
            "confidence": "medium"
        }
    ]
}
with open(out, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
print("สร้างแล้ว:", out)
print("ตรวจด้วย: python3 scripts/validate_findings.py", os.path.relpath(out, ROOT))
