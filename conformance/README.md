# conformance

**ข้อยกเว้นเดียวของ [ADR-0008](../decisions/0008-reference-stack.md)** — โฟลเดอร์เดียวใน repo นี้ที่มี code ได้

ขอบเขตกำหนดโดย [ADR-0011](../decisions/0011-conformance-automation.md) และ**บังคับด้วยความตั้งใจ ไม่ใช่ด้วยเครื่อง** — ถ้ามันเริ่มโต นั่นคือสัญญาณให้ทบทวน ADR ไม่ใช่ให้ขยายเงียบ ๆ

## ใช้ยังไง

```bash
# ดึง manifest จาก repo ต้นทางผ่าน raw.githubusercontent
python3 conformance/drift_check.py

# ใช้ clone ในเครื่องแทน (offline / ทดสอบก่อนต้นทาง merge)
python3 conformance/drift_check.py --local /path/to/devfactory-core
```

ต้องมี `pyyaml` `jsonschema` `referencing` · **ไม่มี `requirements.txt` โดยตั้งใจ** — pin ไว้ใน [workflow](../.github/workflows/drift-check.yml) แทน เพราะ ADR-0008 ห้าม dependency manifest ใน repo นี้

`exit 1` เมื่อมี FAIL · `exit 0` เมื่อมีแค่ WARN

## ตรวจอะไร

| # | ตรวจ | จับ |
| --- | --- | --- |
| 1 | `derived_from.semantics_version` เทียบต้นทาง | ต้นทางขยับ semantics แล้วเราไม่ตาม |
| 2 | `frozen` vocabulary — ขาดค่าที่บังคับ · เกินเมื่อ `closed: true` | ลบ event type ที่ต้องมี · **เพิ่ม decision type เข้าชุดปิด** |
| 3 | จำนวน guarantees | ถอน guarantee เงียบ ๆ |
| 4 | `consumers.md` เทียบ `platform-contract.yaml` จริง | registry ตามหลัง manifest |
| 5 | ตาราง version usage | ตารางอ่านว่าปิด version ได้ทั้งที่มีคน pin |
| 6 | schema draft 2020-12 · `$ref` · `CHANGELOG.md` | contract พังหรือชี้ไปไม่มีอะไร |
| 7 | profile ทุกตัวกับ `contracts/profile/v1` | profile หลุด schema |

**ข้อ 1–3 auto-discover จากบล็อก `derived_from`** — เพิ่ม derived contract ใหม่แล้วครอบคลุมเองทันที ไม่ต้องแก้ checker

**ข้อ 4 อ่านแถวใน `consumers.md` จริง ๆ ไม่ใช่ค้นทั้งไฟล์** — เวอร์ชันแรกของ check นี้ถามแค่ว่าชื่อ contract โผล่ที่ไหนสักแห่งไหม ซึ่งได้ ✅ ปลอมเพราะคำว่า `approval` โผล่ในย่อหน้าอื่นอยู่แล้ว

## ⚠️ เพิ่ม check ใหม่ต้องมี negative test

check ที่ไม่เคยเห็นสถานะ FAIL คือ check ที่ยังไม่รู้ว่าทำงาน — และ check ที่หลวมอันตรายกว่าไม่มี check เพราะสร้างความมั่นใจปลอม

วิธีทดสอบ: แก้ไฟล์ให้ผิดชั่วคราว → รัน → ต้องเห็น FAIL ที่ตรงกับสิ่งที่แก้ → `git checkout` คืน

ชุดที่ใช้ตอนสร้าง checker นี้ ทั้ง 5 เคส FAIL ตามคาด:

| เคส | ผลที่ต้องได้ |
| --- | --- |
| pin `semantics_version` ผิดเวอร์ชัน | `derived: pin=1.0 แต่ต้นทาง=1.1` |
| ลบ `TASK_ASSIGNED` ออกจาก event enum | `frozen: ขาดค่าที่ต้นทางบังคับ` |
| เพิ่ม `AUTO_APPROVE` เข้า decision enum | `frozen: ต้นทาง closed=true แต่มีค่าเกิน` |
| ลบ pin ออกจากแถวใน `consumers.md` | `registry: แถวนี้ขาด pin` |
| ลบ guarantee ออกจาก schema | `frozen: guarantees มี 1 ข้อ ต้นทางบังคับ 3` |

เคสที่สามคือ `AUTO_APPROVE` ที่ [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) ยกมาเป็นเหตุผลว่าทำไม decision vocabulary ต้องเป็นชุดปิด — เป็นเส้นทางที่เปิดได้ด้วยการ *เพิ่ม* ค่าอย่างเดียว โดยไม่ต้องลบหรือเปลี่ยนชื่ออะไรเลย

## FAIL แล้วทำยังไง

**ห้าม disable check เพื่อให้ผ่าน** — FAIL คือ out of conformance ตาม [ADR-0006](../decisions/0006-contract-versioning.md)

| FAIL ที่ | แก้ยังไง |
| --- | --- |
| `derived` — pin ไม่ตรง | อ่าน RFC ที่ต้นทางว่าเปลี่ยนอะไร แล้วอัปเดต schema + `derived_from` ให้ตรง |
| `frozen` — ขาด/เกิน | ถ้าตั้งใจให้ต่าง ต้องมี RFC ที่ต้นทางก่อน (semantic change ตาม RFC-0005 Rule 2) |
| `registry` | อัปเดต `architecture/consumers.md` ให้ตรง manifest |
| `schema` / `profile` | แก้ไฟล์ที่พัง |
