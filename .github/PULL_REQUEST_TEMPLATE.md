## สิ่งที่เปลี่ยน

<!-- ตาราง/คอลัมน์ที่วิเคราะห์ และสิ่งที่พบ -->

## หลักฐาน

- ไฟล์ที่อ้างอิง: `data/tables/....json`
- หน้า PDF: <!-- หน้าใน PDF ต้นฉบับ -->
- ข้อความจริงที่เป็นหลักฐาน (วางใน code block):

```
```

## การตรวจสอบ

```bash
python3 scripts/validate_findings.py analysis/findings/<ไฟล์ของคุณ>.json
```

- [ ] ผ่าน validate_findings.py
- [ ] ไม่มีข้อมูลส่วนบุคคลจริงในไฟล์ที่เพิ่ม
- [ ] ทุกข้อมูล `falsifiable_test` และ `source.pdf_page`
- [ ] ตรวจขอบเขต (scope) ของทุกการอ้างอิงคอลัมน์แล้ว ตาม `docs/reading-the-pdf.md`
- [ ] ไม่ซ้ำกับ `analysis/findings/000-baseline-quality.json`
