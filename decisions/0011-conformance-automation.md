# ADR-0011: Conformance Automation

**Status:** Accepted (2026-08-18)
**Date:** 2026-08-18
**Supersedes:** ส่วน "check `derived_from` ตอน contract change ก็พอ" ใน [ADR-0006](0006-contract-versioning.md)
**Amends:** [ADR-0008](0008-reference-stack.md) — เพิ่มข้อยกเว้นที่มีขอบเขตชัด

## Context

[ADR-0006](0006-contract-versioning.md) ตอบคำถามของ `devfactory-core` ว่าจะ check `derived_from` อัตโนมัติไหม ด้วยคำว่า **"ตรวจตอน contract change ก่อน ยังไม่ทำ CI"** พร้อมเงื่อนไขทบทวน 3 ข้อ:

> derived contract เกิน 5 ตัว · มี repo ต้นทางมากกว่าหนึ่งแห่ง · หรือเคยพลาดจน `semantics_version` ค้างจริงหนึ่งครั้ง

ภายในวันเดียวหลังจากนั้นเกิดสองเรื่อง:

1. **`semantics_version` ขยับจริง 1.0 → 1.1** จาก [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) — และ**โครงของ `contract-semantics.yaml` เปลี่ยนไปด้วย** (`decision_types` จาก list กลายเป็น `{closed, values}`) ไม่ใช่แค่ค่าข้างใน
2. **`consumers.md` ตามหลัง manifest หนึ่งรอบ** — `devfactory-core` เพิ่ม pin `approval/v1` และ `event/v1` ทันทีที่ publish แต่ registry ยังเขียนว่า 4 ตัว · ตาราง version usage จึงอ่านได้ว่า **ปิด `approval/v1` ได้** ทั้งที่มี repo pin อยู่จริง ซึ่งเป็นคำถามเดียวที่ตารางนั้นมีอยู่เพื่อตอบ

เรื่องที่ 2 หลุดสายตาไปหนึ่งรอบทั้งที่ตรวจด้วยคน และตอนตรวจซ้ำก็เกือบหลุดอีกเพราะ check ฉบับแรกถามแค่ว่า "ชื่อ contract โผล่ที่ไหนสักแห่งในไฟล์ไหม" — คำว่า `approval` โผล่ในย่อหน้าอื่นอยู่แล้ว จึงได้ ✅ ปลอม

เงื่อนไขข้อ 3 จึงถือว่าเข้าแล้วในทางปฏิบัติ

## Problem Statement

การตรวจด้วยคนล้มเหลวสองแบบที่ต่างกัน และทั้งสองแบบเกิดขึ้นจริงแล้ว:

* **ไม่ได้ตรวจ** — repo ต้นทางขยับ `semantics_version` โดยที่ไม่มีอะไรใน repo นี้เปลี่ยน จึงไม่มีเหตุการณ์อะไรมากระตุ้นให้ใครไปตรวจ
* **ตรวจแล้วแต่หลวมเกิน** — check ที่เขียนเร็ว ๆ ให้ผลผ่านโดยไม่ได้ตรวจสิ่งที่ตั้งใจ ซึ่งอันตรายกว่าไม่มี check เพราะสร้างความมั่นใจปลอม

แต่ [ADR-0008](0008-reference-stack.md) ห้าม implementation ใน repo นี้ และ [ADR-0001](0001-platform-scope.md) กำหนดว่าเก็บได้แค่ contract / architecture / decision

## Options

### A. คงการตรวจด้วยคนต่อไป

* ✅ ไม่ต้องแตะ ADR-0008
* ❌ ล้มเหลวไปแล้วสองแบบภายในวันเดียว และจะแย่ลงเมื่อมี consumer มากกว่าหนึ่งราย
* ❌ `semantics_version` ที่ขยับโดยฝั่งเราไม่ขยับ ไม่มีอะไรกระตุ้นให้ตรวจเลย

### B. ย้าย checker ไป repo แยก

* ✅ ADR-0008 ไม่ต้องแก้เลย
* ❌ checker ที่แยกจาก contract จะ drift จาก contract เอง — เป็นปัญหาเดียวกับที่ ADR-0006 สร้างขึ้นมาแก้
* ❌ repo ใหม่ต้องมี CI, สิทธิ์, และคนดูแลของตัวเอง เพื่อไฟล์เดียว

### C. เก็บ checker ไว้ใน repo นี้ภายใต้ขอบเขตที่เขียนไว้ชัด ⭐

* ✅ checker อยู่ข้าง contract ที่มันตรวจ — แก้ contract แล้วเห็นทันทีว่าต้องแก้ check ไหม
* ✅ PR ที่ทำให้ drift ถูก block ตั้งแต่ก่อน merge ไม่ใช่ไปเจอทีหลัง
* ✅ scheduled run จับกรณีที่ต้นทางขยับฝ่ายเดียว ซึ่งเป็นรูแบบที่คนตรวจไม่มีทางเจอ
* ⚠️ ต้องยอมรับว่ามี code ก้อนแรกใน repo — และต้องกันไม่ให้มันโต

## Decision

**C** — `conformance/` เป็น **ข้อยกเว้นเดียว** ของ ADR-0008 พร้อมขอบเขตที่บังคับได้

**Reason:** การตรวจด้วยคนล้มเหลวจริงแล้วสองแบบ และแบบที่สอง (check หลวมจนได้ ✅ ปลอม) อันตรายกว่าไม่มี check · การแยก repo แก้ปัญหา ADR-0008 ด้วยการสร้างปัญหา drift ชุดใหม่ ซึ่งเป็นสิ่งเดียวกับที่ ADR ชุดนี้มีอยู่เพื่อกัน

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ขอบเขตของ `conformance/`

**ทำได้:**

* อ่านไฟล์ใน repo นี้ และอ่าน manifest จาก repo ต้นทาง/consumer ผ่าน `raw.githubusercontent.com`
* เทียบค่า แล้วรายงานผลผ่าน exit code

**ห้าม:**

* เขียนหรือแก้ไฟล์ใด ๆ — รวมถึง generate schema, generate เอกสาร, อัปเดต registry อัตโนมัติ
* เรียก network host อื่นนอกจาก `raw.githubusercontent.com`
* มี `package.json` · `pyproject.toml` · `requirements.txt` · lockfile · `Dockerfile` — dependency pin ไว้ใน workflow step แทน
* โตเกินไฟล์เดียว ถ้าต้องแตกเป็นหลายไฟล์เมื่อไหร่ ให้ทบทวน ADR นี้ก่อน
* กลายเป็นที่รวม utility อื่น — `conformance/` ไม่ใช่ `scripts/`

### สิ่งที่ตรวจ

| # | ตรวจอะไร | จับอะไรได้ |
| --- | --- | --- |
| 1 | `derived_from.semantics_version` เทียบ manifest ต้นทาง | ต้นทางขยับ semantics แล้วเราไม่ตาม |
| 2 | `frozen` vocabulary — ขาดค่าที่บังคับ · เกินค่าเมื่อ `closed: true` | ลบ event type ที่ต้องมี · เพิ่ม decision type เข้าชุดปิด |
| 3 | จำนวน guarantees ครอบคลุมของต้นทาง | ถอน guarantee เงียบ ๆ |
| 4 | `consumers.md` เทียบ `platform-contract.yaml` จริงของ consumer | registry ตามหลัง manifest |
| 5 | ตาราง version usage ครอบคลุม contract ที่ถูก pin | ตารางอ่านว่าปิด version ได้ทั้งที่มีคน pin |
| 6 | schema ถูกต้องตาม draft 2020-12 · `$ref` resolve ครบ · มี `CHANGELOG.md` | contract พังหรือชี้ไปไม่มีอะไร |
| 7 | profile ทุกตัว validate กับ `contracts/profile/v1` | profile หลุดจาก schema |

ข้อ 1–3 **auto-discover จากบล็อก `derived_from`** — เพิ่ม derived contract ใหม่แล้วครอบคลุมเองโดยไม่ต้องแก้ checker

### เมื่อไหร่ที่รัน

| trigger | เหตุผล |
| --- | --- |
| `pull_request` | block PR ที่ทำให้ drift ก่อน merge |
| `push` → `main` | จับกรณีที่ push ตรง |
| `schedule` รายวัน | **จับกรณีที่ต้นทางขยับฝ่ายเดียว** ซึ่ง trigger จาก repo เราจับไม่ได้เลย |
| `workflow_dispatch` | ตรวจตามต้องการ |

### FAIL หมายถึงอะไร

FAIL = **out of conformance** ตาม ADR-0006 — ต้องแก้ให้ตรง หรือถ้าตั้งใจให้ต่าง ต้องมี ADR/RFC รองรับก่อน · ห้าม disable check เพื่อให้ผ่าน

## Consequences

* repo นี้มี code ก้อนแรก — `conformance/drift_check.py` และ workflow ที่เรียกมัน
* ADR-0008 ยังใช้ได้ทั้งหมด **ยกเว้น** `conformance/` ตามขอบเขตข้างบน · `contracts/` ยังเป็น YAML/JSON Schema ล้วนเหมือนเดิม
* checker ต้องมี **negative test** ก่อนเชื่อว่ามันทำงาน — ตอนเพิ่ม check ใหม่ทุกครั้งต้องพิสูจน์ว่ามัน FAIL ได้จริงกับกรณีที่ควร FAIL
* consumer ที่เพิ่มเข้ามาใน `consumers.md` พร้อม manifest จะถูกตรวจอัตโนมัติทันที ไม่ต้องแก้ checker
* ถ้า `conformance/` เริ่มโตเกินหนึ่งไฟล์ หรือมีคนอยากให้มัน generate อะไร → นั่นคือสัญญาณให้ทบทวน ADR นี้ ไม่ใช่ให้ขยายขอบเขตเงียบ ๆ

## Sources

[ADR-0006](0006-contract-versioning.md) · [ADR-0008](0008-reference-stack.md) · [`devfactory-core` RFC-0005 Rule 3](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) · [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) · [`ref/rfc-0009-vocabulary-extension.md`](../ref/rfc-0009-vocabulary-extension.md)
