# ADR-0012: Consent Contract

**Status:** Accepted (2026-08-19)
**Date:** 2026-08-19
**Depends on:** [ADR-0001](0001-platform-scope.md) · [ADR-0006](0006-contract-versioning.md) · [ADR-0007](0007-multi-tenancy.md) · [ADR-0010](0010-risk-approval-taxonomy.md)
**Blocking:** [issue #15](https://github.com/monthop-gmail/agent-platform/issues/15) · `contracts/consent/` (ยังไม่มี)

## Context

[`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) — consumer ตัวแรกที่ conform จริง — เสนอ contract ใหม่ที่ตอบคำถาม **"ใครยอมให้ใครเข้าถึงข้อมูลของใคร อะไรบ้าง เพื่ออะไร นานแค่ไหน"** ([#15](https://github.com/monthop-gmail/agent-platform/issues/15))

เขา **มี implementation ใช้อยู่แล้ว** (`contracts/consent/v1` ในบ้านตัวเอง + [ADR-0007](https://github.com/monthop-gmail/care-agent-platform/blob/main/decisions/0007-consent-and-data-access.md)) และเก็บให้ domain-free ตั้งแต่แรกโดยมีเทสบังคับว่าใช้ `subject_id` ไม่ใช่ `patient_id` · เขาระบุเองว่า **ไม่รีบ** เปิด issue ไว้ให้ตัดสินตอนมี consumer ตัวที่สอง

### ช่องว่างที่ contract ปัจจุบันตอบไม่ได้

`policy/v1` ตอบว่า *"identity นี้ทำ action นี้ได้ไหม"* แต่ตอบไม่ได้ว่า **"กับข้อมูลของคนไหน"**

```text
ลูกสาวมีสิทธิ์ medication.read     ← policy/v1 ตอบได้
อ่านได้เฉพาะยาของแม่ตัวเอง          ← ไม่มี contract ไหนตอบได้
```

และ `policy/v1` `Decision` ไม่มีที่ให้บอกว่า *"อนุญาตเพราะ consent ไหน"* — audit ตอบได้แค่ว่า policy ไหนอนุญาต แต่ตอบไม่ได้ว่าความยินยอมข้อไหนรองรับการเข้าถึงครั้งนั้น

`enterprise-knowledge` จะเจอคำถามเดียวกันทุกครั้งที่ทำ ACL-aware retrieval — ถ้าต่างคนต่างนิยาม audit ข้าม repo จะเทียบกันไม่ได้ ซึ่งเป็นปัญหาที่ [ADR-0006](0006-contract-versioning.md) มีอยู่เพื่อกัน

### เรื่องที่ต้องระวัง

`profile/v1` เคยถูกเพิ่มนอกลิสต์ P0 มาแล้วหนึ่งครั้ง (บันทึกไว้ใน [`contracts/README.md`](../contracts/README.md)) · ตัวนี้จะเป็นตัวที่สอง — ถ้ารับทุกคำขอที่ *มีเหตุผลดี* ลิสต์ P0 จะไม่มีความหมาย ADR นี้จึงต้องตอบด้วยว่า **เกณฑ์อะไรที่ทำให้คำขอผ่าน** ไม่ใช่แค่ว่าคำขอนี้ผ่าน

## Options

### A. รับเข้าเป็น `contracts/consent/v1` — platform เป็นเจ้าของทั้ง semantics และ schema ⭐

* ✅ ตอบคำถามที่ไม่มี contract ไหนตอบได้ และเป็นคำถามที่ทุก repo ที่ถือข้อมูลบุคคลต้องตอบ
* ✅ อยู่ตระกูลเดียวกับ `policy/v1` และ `approval/v1` — governance ไม่ใช่ infra · ทีม pstack สรุปแล้วว่าไม่ควรอยู่ใน kernel ของ runtime ([pstack#3](https://github.com/willpower-institute/pstack/issues/3))
* ✅ มี reference implementation ที่รันจริงและ domain-free อยู่แล้ว — ไม่ใช่ contract ที่ออกแบบจากจินตนาการ
* ✅ audit ข้าม repo เทียบกันได้ ซึ่งเป็นเหตุผลตั้งต้นของการมี contract กลาง
* ❌ contract ที่สองที่เพิ่มนอกลิสต์ P0 — ต้องมีเกณฑ์กันไม่ให้กลายเป็นนิสัย
* ⚠️ platform ต้องรับผิดชอบ semantics ของ consent เอง (ต่างจาก `approval`/`event` ที่ semantics อยู่ที่ `devfactory-core`) — ต้องมั่นใจว่าเข้าใจเรื่องนี้พอ

### B. ไม่รับ — ให้แต่ละ domain repo นิยามเอง

* ✅ ลิสต์ contract ไม่โต · platform ไม่ต้องรับผิดชอบ semantics ที่ไม่ถนัด
* ❌ `care` และ `enterprise-knowledge` จะนิยามคนละแบบ แล้ว audit ข้าม repo เทียบไม่ได้ — เป็นความล้มเหลวแบบเดียวกับ "schema เดียวกันคนละ field" ที่ ADR-0006 สร้างขึ้นมาแก้
* ❌ ผลักงานยากไปให้ consumer ทุกราย ทั้งที่เป็นคำถามเดียวกัน

### C. ขยาย `policy/v1` ให้ครอบ consent แทนการมี contract ใหม่

* ✅ ไม่เพิ่ม contract
* ❌ **ผิดโดยโครงสร้าง** — `policy/v1` `Decision` เป็นผลการประเมิน *ครั้งหนึ่ง* ที่มีอายุสั้นและ `expires_at` สั้น · consent เป็น *ข้อเท็จจริงที่คงอยู่* ข้ามหลาย request หลายเดือน และถูกเพิกถอนได้เป็นเหตุการณ์ของตัวเอง
* ❌ ยัดรวมแล้ว `revoked_at` จะไปอยู่ใน object ที่ควร immutable ซึ่งขัดกับ `policy/v1` ที่ห้ามนำ decision ที่หมดอายุกลับมาใช้

### D. รับหลักการ แต่เลื่อน schema ไว้จนมี consumer ตัวที่สองที่ต้องใช้จริง

* ✅ ตรงกับที่ผู้ขอเขียนเองว่า *"ไม่รีบ · เปิดไว้เพื่อให้ตัดสินใจได้ตอนที่มี consumer ตัวที่สอง"*
* ✅ ป้องกันการออกแบบ contract จาก consumer รายเดียว ซึ่งเป็นวิธีที่ทำให้ contract กลางกลายเป็น schema ของ domain แรกที่มาถึง
* ❌ `care` ต้องแบก `known_gaps` ต่อไป และเมื่อ `enterprise-knowledge` มาถึงก็ต้อง migrate ของที่รันอยู่แล้ว
* ⚠️ ถ้าเลือกทางนี้ ต้องระบุว่า *"consumer ตัวที่สอง"* คือเงื่อนไขที่ตรวจได้ ไม่ใช่คำที่เลื่อนได้เรื่อย ๆ

## เกณฑ์รับ contract ใหม่ (ต้องตอบก่อนตัดสิน)

ถ้ารับ ADR นี้ต้องวางเกณฑ์ไว้ด้วย ไม่ใช่ตัดสินเฉพาะกรณี · เสนอ 4 ข้อ — **ต้องครบทุกข้อ**:

| # | เกณฑ์ | `consent/v1` |
| --- | --- | --- |
| 1 | มี contract ที่มีอยู่แล้วตอบคำถามนี้ได้หรือไม่ — ถ้ามี ให้ขยายตัวนั้น | ❌ ไม่มี · `policy/v1` ตอบคนละคำถาม (ดู option C) |
| 2 | จะมี consumer อย่างน้อย 2 รายที่ต้องใช้ หรือมี 1 รายที่ใช้จริงแล้วและรายที่สองระบุตัวได้ | ✅ `care` ใช้จริง · `enterprise-knowledge` ระบุตัวได้และเจอคำถามเดียวกัน |
| 3 | มี implementation จริงให้อ้าง ไม่ใช่ออกแบบจากจินตนาการ | ✅ `care/contracts/consent/v1` + ADR-0007 · domain-free โดยมีเทสบังคับ |
| 4 | platform เข้าใจ semantics พอที่จะเป็นผู้ตัดสินสุดท้าย หรือมีเจ้าของ semantics ที่ชัด | ⚠️ **ข้อที่ต้องเคาะ** — ดูหัวข้อถัดไป |

## ถ้ารับ — ใครเป็นเจ้าของ semantics

[ADR-0006 C2](0006-contract-versioning.md) ตั้งบรรทัดฐานว่า **repo ที่มีความรู้เรื่องนั้นเป็นเจ้าของ semantics** ส่วน platform เป็นเจ้าของ wire schema · ใช้กับ consent ได้ 2 แบบ:

| แบบ | semantics | ผล |
| --- | --- | --- |
| **D1. platform เป็นเจ้าของทั้งคู่** | `agent-platform` | consent เป็น governance เหมือน `policy/v1` ซึ่ง platform เป็นเจ้าของอยู่แล้ว · แก้ได้ผ่าน ADR ที่นี่ ไม่ต้องรอ repo ไหน |
| **D2. `care` เป็นเจ้าของ semantics** | `care-agent-platform` | ตามแบบ `devfactory-core` · แต่ consent ไม่ใช่เรื่องเฉพาะ care และ `enterprise-knowledge` จะต้องไปขอ RFC ที่ care สำหรับ field ที่ care ไม่มีความเห็นด้วย — เป็นปัญหาเดียวกับที่ RFC-0005 ปฏิเสธ A2/B2 |

**เสนอ D1** — consent เป็น governance ระดับ platform ไม่ใช่ความรู้เฉพาะโดเมน · `Scope` และ `Purpose` เป็นค่าของโดเมนอยู่แล้ว (platform กำหนดแค่ว่าเป็น string ที่ตกลงกันใน tenant นั้น) ส่วนที่เหลือคือ *ใคร ให้ใคร เมื่อไร ถอนเมื่อไร* ซึ่งเป็นรูปแบบเดียวกันทุกโดเมน

## ช่องว่างที่เจอในร่างของผู้ขอ

ถ้ารับ ต้องปิด 4 จุดนี้ก่อน publish:

1. 🔴 **ไม่มี `revoked_by`** — ร่างมีแค่ `revoked_at` · การเพิกถอนต้องบันทึกว่า **ใครถอน** ด้วยเหตุผลเดียวกับที่ `granted_by` เป็น required · *"ความยินยอมนี้ถูกถอนแล้ว"* ไม่ใช่ audit record · *"principal นี้ถอนเมื่อเวลานี้"* คือ audit record
2. 🟠 **`expires_at: null` หมายถึงอะไร** — ต้องระบุว่า *ไม่มีวันหมดอายุ* ไม่ใช่ *ยังไม่ได้กำหนด* · ค่าที่กำกวมในเรื่องนี้อันตราย
3. 🟠 **ไม่มี `revoked_reason`** — ถอนเพราะเจ้าของเปลี่ยนใจ กับถอนเพราะผู้รับละเมิดเงื่อนไข ต่างกันมากตอน audit
4. 🟡 **`purpose` เป็น string เดี่ยว** — ควรเป็น array หรือไม่? consent หนึ่งใบครอบหลายวัตถุประสงค์ได้จริงไหม หรือควรบังคับให้แยกใบ · เอียงไปทาง **บังคับแยกใบ** เพราะ purpose ที่กว้างคือวิธีที่ consent กลายเป็นใบเบิกทางทุกอย่าง

## ⚠️ ขอบเขตที่ต้องเขียนไว้ในตัว contract

**contract นี้บันทึกความยินยอม ไม่ได้ทำให้ความยินยอมนั้นชอบด้วยกฎหมาย** — ความสมบูรณ์ตาม PDPA หรือกฎหมายคุ้มครองข้อมูลอื่นเป็นเรื่องของ implementation และของผู้ควบคุมข้อมูล ไม่ใช่ของ schema

ถ้าไม่เขียนไว้ จะมีคนอ่านว่า "ผ่าน conformance = ทำถูกกฎหมาย" ซึ่งไม่จริงและอันตรายกว่าการไม่มี contract

กฎที่ควรยกจากร่างมาทั้งชุด — ทั้งห้าข้อเป็นสิ่งที่ทำให้ contract นี้มีค่ามากกว่าตาราง:

```text
consent ข้าม tenant ไม่ได้ทุกกรณี
การให้ ใช้ และเพิกถอน ต้องออก audit event ทุกครั้ง
การเพิกถอนมีผลทันที ไม่ใช่รอ session หมดอายุ
grant ที่หมดอายุหรือถูกเพิกถอนแล้ว ห้ามนำกลับมาใช้ซ้ำ ต้องสร้างใหม่
ความสัมพันธ์ (ญาติ/ผู้ดูแล/ทีมเดียวกัน) ไม่ให้สิทธิ์อะไรโดยอัตโนมัติ
```

ข้อสุดท้ายสำคัญที่สุด — เป็นสิ่งที่ทำให้ consent เป็น *ข้อเท็จจริงที่ชัดเจน* ไม่ใช่ *สิ่งที่อนุมานจากความสัมพันธ์*

## Decision

**A + D1** — รับเข้าเป็น `contracts/consent/v1` โดย **`agent-platform` เป็นเจ้าของทั้ง semantics และ wire schema** · เกณฑ์รับ contract ใหม่ 4 ข้อ **ยืนยันตามที่เสนอ**

**Reason:** ไม่มี contract ไหนตอบคำถาม *"กับข้อมูลของคนไหน"* ได้ และเป็นคำถามที่ทุก repo ที่ถือข้อมูลบุคคลต้องตอบ — ถ้าต่างคนต่างนิยาม audit ข้าม repo จะเทียบกันไม่ได้ ซึ่งเป็นความล้มเหลวแบบเดียวกับที่ ADR-0006 มีอยู่เพื่อกัน · ปฏิเสธ C เพราะ `policy/v1` `Decision` เป็นผลประเมินครั้งหนึ่งที่อายุสั้น ส่วน consent เป็นข้อเท็จจริงที่คงอยู่และถูกเพิกถอนเป็นเหตุการณ์ของตัวเอง · ปฏิเสธ D เพราะ implementation ที่ยกขึ้นได้มีอยู่แล้วและ domain-free จริง การรออีกฝ่ายมาถึงทำให้ต้อง migrate ของที่รันอยู่โดยไม่ได้ข้อมูลใหม่ที่เปลี่ยนคำตอบ

**เจ้าของ semantics = platform (D1):** consent ไม่ใช่ความรู้เฉพาะโดเมน — `Scope` และ `Purpose` เป็นค่าของโดเมนอยู่แล้ว ส่วนที่เหลือคือ *ใคร ให้ใคร เมื่อไร ถอนเมื่อไร* ซึ่งเป็นรูปแบบเดียวกันทุกโดเมน · ถ้าให้ `care` ถือแบบ `devfactory-core` จะทำให้ `enterprise-knowledge` ต้องขอ RFC ที่ `care` สำหรับ field ที่ `care` ไม่มีความเห็นด้วย ซึ่งเป็นปัญหาที่ RFC-0005 ปฏิเสธ A2/B2 มาแล้ว

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### เกณฑ์ 4 ข้อมีผลกับคำขอ contract ใหม่ทุกครั้งจากนี้

ต้องครบทุกข้อ ไม่ใช่ส่วนใหญ่ · บันทึกไว้ใน [`contracts/README.md`](../contracts/README.md) เพื่อให้ผู้ขอวัดตัวเองได้ก่อนเปิด issue

## Consequences

* `contracts/consent/v1/consent.schema.yaml` + `CHANGELOG.md` · **ไม่มี** `derived_from` เพราะ semantics เป็นของที่นี่
* ปิดช่องว่าง 4 จุดข้างบนก่อน publish · เพิ่ม `revoked_by` เป็น required เมื่อมี `revoked_at`
* `policy/v1` `Decision` เพิ่ม optional `consent_id` — **แยกเป็นการเปลี่ยนอีกครั้ง** ไม่รวมในนี้ เพื่อให้ `consent/v1` ยืนได้เองก่อน
* `contracts/README.md` บันทึกว่าเป็น contract ที่สองที่เพิ่มนอกลิสต์ P0 **พร้อมเกณฑ์ 4 ข้อ** ที่ทำให้ผ่าน — เพื่อให้คำขอต่อไปวัดด้วยเกณฑ์เดียวกัน ไม่ใช่ด้วยความน่าเชื่อของผู้ขอ
* `care-agent-platform` ถอด `no-consent-contract` ออกจาก `gaps` แล้ว pin `consent/v1` ได้
* drift check ครอบคลุมเองทันทีในส่วน schema validity และ `CHANGELOG` · ส่วน `frozen`/`binding` ไม่มีผลเพราะไม่ใช่ derived contract

## Sources

[issue #15](https://github.com/monthop-gmail/agent-platform/issues/15) · [`care-agent-platform` ADR-0007](https://github.com/monthop-gmail/care-agent-platform/blob/main/decisions/0007-consent-and-data-access.md) · [`care-agent-platform/platform-contract.yaml`](https://github.com/monthop-gmail/care-agent-platform/blob/main/platform-contract.yaml) `gaps.no-consent-contract` · [ADR-0006 C2](0006-contract-versioning.md) · [ADR-0010](0010-risk-approval-taxonomy.md)
