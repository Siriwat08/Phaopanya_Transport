# โครงสร้างข้อมูล (data model)

แอปมี **2,742 อ็อบเจกต์** แบ่งเป็น 6 ชนิด

| type | จำนวน | คืออะไร |
|---|---|---|
| `table` | 90 | ตาราง — 30 ตารางจริง + 60 ตารางของบอท (Process Table / Output) |
| `column` | 2,304 | คอลัมน์ พร้อมคุณสมบัติและสูตรครบ |
| `action` | 214 | แอคชัน (bulk action / bot action) |
| `view` | 115 | วิว (มีแบบ Grid / Form / Detail / Deck) |
| `slice` | 8 | สไลซ์ = มุมมองเฉพาะแถวของตาราง พร้อมเงื่อนไขกรอง |
| `format_rule` | 11 | กฎจัดรูปแบบแถวตามเงื่อนไข |

## โดเมนการใช้งาน (11 โดเมน)

| code | ชื่อ | ตารางจริง | สิ่งที่อยู่ในโดเมน |
|---|---|---|---|
| D01 | งานจัดส่งหลัก | 8 | รับงาน → จัดเส้นทาง → ส่ง → ปิดงาน |
| D02 | การวางบิลและราคา | 6 | เรทดีเซล ราคาตามระยะทาง ใบวางบิล |
| D03 | เบิกค่าและส่วนต่าง | 3 | คืนเงิน/เบิกเงิน เบิกส่วนต่างรายเที่ยว |
| D04 | บำรุงรักษารถ | 1 | เข้าซ่อม อาการชำรุด รูปหลักฐาน |
| D05 | เอกสารและการสแกน | 6 | สแกนเอกสาร ใบเสร็จ คืนเอกสารเข้าคลัง |
| D06 | แจ้งปัญหาระหว่างวัน | 1 | แจ้งปัญหาที่จุดส่ง + รูป/พิกัด |
| D07 | พนักงานและข้อมูลบุคคล | 1 | ข้อมูลพนักงาน ทะเบียนรถ สิทธิ์อนุมัติ |
| D08 | ประกาศและการรับทราบ | 2 | ประกาศประจำวัน + ลงชื่อรับทราบ |
| D09 | หน้าจอหลักและภาพรวม | 1 | หน้าหลักผู้บริหาร |
| D10 | ตั้งค่าระบบผู้ใช้ | 1 | ค่าตั้งเฉพาะผู้ใช้ |
| D11 | บอทและกระบวนการอัตโนมัติ | — | บอท 30 ตัว + ตาราง Process/Output 60 ตาราง |

## คุณสมบัติของคอลัมน์ที่ต้องรู้

`props` ของคอลัมน์มีคีย์เหล่านี้ (ค่าว่าง = ไม่ได้ตั้ง)

| key | หมายเหตุ |
|---|---|
| `Column name` | ชื่อคอลัมน์ (case sensitive) |
| `Type` | Text / Number / DateTime / Enum / EnumList / Ref / Image / Signature / Dropdown … |
| `Type Qualifier` | **JSON string** — รวม Valid_If, Show_If, Required_If, Editable_If, Reset_If, EnumValues, ReferencedTableName, ReferencedTypeQualifier |
| `App formula` | สูตรหลักที่คำนวณอัตโนมัติทุกแถว |
| `Initial value` | ค่าเริ่มต้นตอนสร้างแถว (**คำนวณครั้งเดียวแล้วค้าง**) |
| `Read-Only` / `Editable?` | ควบคุมการแก้ไข |
| `Key` / `Part of Key?` | คีย์หลักของตาราง |
| `Sensitive data` | ข้อมูลส่วนบุคคล — ควรเป็น Yes |
| `Searchable` / `Scannable` | ค้นหา/สแกนได้ |
| `Editable Initial Value?` | ให้ผู้ใช้แก้ค่าเริ่มต้นได้ |

## คุณสมบัติของตารางที่ต้องรู้

| key | หมายเหตุ |
|---|---|
| `Security filter` | **สิ่งที่ขาดไปใน 6 ตารางจริง** — ควรมีในทุกตาราง |
| `Are updates allowed?` | ALL_CHANGES / ADDS_ONLY / UPDATES_ONLY / READ_ONLY |
| `Expression for update mode` | เงื่อนไขต่อบทบาท — ขาดในหลายตาราง |
| `Source Path` | ตำแหน่งจริงใน Appsheet |

## รูปแบบแอคชัน

`With these properties` เป็น JSON string ที่มีคีย์สำคัญ:
- `Assignments[]` → `{ColumnToEdit, NewColumnValue}` (ชื่อคอลัมน์ต้องตรงเป๊ะ มิฉะนั้น error)
- `ReferencedRows` → สูตรเลือกแถวที่ action จะทำงานด้วย
- `ReferencedAction` → ชื่อ action ที่เรียก (REF_ACTION)
- `Prominence` / `BulkApplicable` / `Do this` / `Conditions`

## โครงสร้างบอท (D11)

```
แอคชันแบบ SET_COLUMN_VALUE
   └─ ตั้ง ชื่องาน = <ชื่องานที่ต้องการ>
   └─ ตั้ง ปริ๊นใบวางบิลแยกตามชื่องาน = TRUE
        └─ บอท "Process for <ชื่องาน> Process Table" ทำงาน
             ├─ เขียนผลลง "… Output" (ตารางสถานะขั้นกลาง)
             └─ ปล่อยแฟล็ก "ปริ๊นใบวางบิลแยกตามชื่องาน" = FALSE
```

- บอท 30 ตัว · ตาราง Process 30 ตาราง · ตาราง Output 30 ตาราง
- `ปริ๊นใบวางบิลทุกงาน` เป็น COMPOSITE ขนาด 38 ขั้น
- `Process_Delivery_Status_Bot Action - 1` เป็น REF_ACTION → `Mark_As_Delivered`
