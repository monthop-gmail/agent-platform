# ADR-0023: binding ที่ resolve แล้วบันทึกไว้ได้ — ถ้า identity ของสิ่งที่ build ครอบมัน

**Status:** Accepted (2026-09-02)
**Date:** 2026-09-02
**Depends on:** [ADR-0009](0009-capability-model.md) · [ADR-0006](0006-contract-versioning.md) · [ADR-0022](0022-agent-may-narrow-its-own-scope.md)
**Blocking:** [issue #46](https://github.com/monthop-gmail/agent-platform/issues/46) · `contracts/model/v1`

## Context

[`agent-builder-dsh-poc`](https://github.com/monthop-gmail/agent-builder-dsh-poc) ผลิต `CompiledAgent` — package ที่มี model binding ติดอยู่ข้างในตั้งแต่ตอน build แล้วรันได้บน runtime หลายตัว

`model/v1` `Request.model_id` เขียนไว้ว่า:

> "ห้าม hard-code รายชื่อ model ไว้ใน **task schema** — ระบุตอน runtime เท่านั้น
> การเลือก model เป็นหน้าที่ของ routing ตาม capability (ADR-0009)"

ประโยคนี้ทำให้ผู้ขอต้องมาถามว่าเขาทำผิดหรือเปล่า และ **consumer รายถัดไปที่อ่านจะสรุปว่าเขาทำผิด** ทั้งที่ ADR-0009 ไม่เคยพูดถึงเรื่องนี้เลย

> 🔒 ADR ฉบับนี้ **ไม่รื้อ [ADR-0009](0009-capability-model.md)** — capability-first ยังเป็นหลัก · ที่ตอบคือคำถามคนละข้อ: *ผลของการ resolve บันทึกไว้ได้ไหม*

## ประโยคที่มีปัญหาพูดถึง "task schema" ไม่ใช่ "สิ่งที่ build แล้ว"

สองอย่างนี้คนละชนิดกัน และการรวมเข้าด้วยกันคือที่มาของความสับสน:

| | คืออะไร | ใครเขียน |
| --- | --- | --- |
| **task schema / request** | คำประกาศว่า *จะให้ทำอะไร* | คน หรือ agent definition |
| **build artifact** | บันทึกว่า *การ resolve ให้ผลอะไร* | เครื่อง จากการ resolve |

```text
package.json      ประกาศช่วง            ←  capability_requirement
package-lock.json บันทึกผลที่ resolve   ←  CompiledAgent
```

**ไม่มีใครคิดว่า lockfile ละเมิดหลัก "อย่า hard-code version"** เพราะมันไม่ใช่คำประกาศ มันคือหลักฐานว่าอะไรถูกเลือก · การห้ามบันทึกผลการ resolve จะทำให้ **build ที่ทำซ้ำได้เป็นไปไม่ได้** และผลักให้คน hard-code จริง ๆ แทน ซึ่งแย่กว่า

## แต่ผู้ขอเจอบั๊กของตัวเองระหว่างเขียน issue — และนั่นสำคัญกว่าคำถามแรก

> `manifestChecksum` คำนวณจาก **manifest** ไม่ใช่จากผลของการ resolve
> ถ้า catalog เปลี่ยน (model ถูก deprecate · provider เป็น `degraded` · มีตัวที่ถูกกว่าเข้ามา)
> **checksum เท่าเดิมแต่ agent รันด้วย model คนละตัว**

เขาใช้ `manifestChecksum` ที่เท่ากันข้ามทุก target เป็น **ข้อพิสูจน์ portability** — แต่มันพิสูจน์ได้แค่ว่า *manifest* เหมือนกัน ไม่ได้พิสูจน์ว่า *สิ่งที่รัน* เหมือนกัน

**checksum ที่อ้างมากกว่าสิ่งที่มันครอบ** คือ false ✅ ตระกูลเดียวกับที่ repo นี้ไล่ปิดมาตลอด — `sequence` ที่ต่อเนื่องแล้วเชื่อว่า trail ครบ ([ADR-0015](0015-event-sequence-and-trail-closure.md)) · `grant_id` ที่ชี้ไปใบที่ประเมินใหม่แล้วเชื่อว่าตอบ audit ได้ ([ADR-0016](0016-recording-which-consent-allowed-access.md))

การตอบว่า "build-time binding ถูกต้อง" โดยไม่พูดเรื่องนี้ **คือการรับรองบั๊กนั้นไปด้วย**

## Options

### A. ไม่รับ — binding ต้องเกิดตอน runtime เท่านั้น

* ✅ ไม่ต้องแก้สัญญา · ถ้อยคำเดิมใช้ได้
* ❌ **build ที่ทำซ้ำได้เป็นไปไม่ได้** — รัน agent เดิมสองครั้งได้ model คนละตัวโดยไม่มีร่องรอย
* ❌ ผลักให้คน hard-code จริง ๆ เพื่อให้ deploy คาดเดาได้ ซึ่งเป็นสิ่งที่ประโยคนั้นตั้งใจกัน
* ❌ ADR-0009 ไม่เคยห้ามเรื่องนี้ — เป็นการอ่านประโยคที่เขียนถึง task schema ให้กว้างเกินที่ตั้งใจ

### B. รับ + แก้ถ้อยคำ + **กฎว่า identity ต้องครอบผลการ resolve** ⭐

* ✅ ปิดความขัดแย้งในสัญญา และปิดบั๊กที่ผู้ขอเจอ **ในการตัดสินเดียว**
* ✅ ไม่แตะ ADR-0009 — capability-first ยังเป็นหลัก binding เป็นเพียงบันทึกของผลลัพธ์
* ✅ `pin_provider` ใน `capability_requirement` มีอยู่แล้วสำหรับกรณีที่ต้อง pin จริง — ทางนี้ต่อยอดจากของเดิม ไม่ใช่ของใหม่
* ❌ กฎเรื่อง identity **บังคับด้วย schema ไม่ได้** — build artifact ไม่ใช่ contract ของเรา

### C. รับแบบไม่มีเงื่อนไข — แก้ถ้อยคำอย่างเดียว

* ✅ สั้นที่สุด · ตอบคำถามที่เขาถามตรง ๆ
* ❌ **รับรอง checksum ที่พิสูจน์สิ่งที่มันไม่ได้ครอบ** ทั้งที่เห็นปัญหาอยู่ตรงหน้า — ถ้าจะให้สิทธิ์ ต้องให้พร้อมเงื่อนไขที่ทำให้สิทธิ์นั้นมีความหมาย

### D. รับ + นิยาม `CompiledAgent` เป็น contract กลาง

* ✅ ทุกคนที่ build agent จะมีรูปเดียวกัน
* ❌ **ตกเกณฑ์ [ADR-0012](0012-consent-contract.md) ข้อ 2 และ 4** — consumer รายเดียว และ platform ไม่ได้เข้าใจ build semantics ดีพอจะเป็นผู้ตัดสินสุดท้าย · ผู้ขอเองก็ไม่ได้ขอ

### E. ไม่ตอบ ปล่อยให้ตีความเอง

* ❌ ประโยคใน `model/v1` จะยังบอกตรงข้ามกับสิ่งที่ถูกต้องต่อไป และรายถัดไปจะสรุปว่าเขาทำผิด

## Decision

**B** — รับ binding ที่แช่แข็งไว้ · แก้ถ้อยคำ `model/v1` · และบังคับว่า identity ของสิ่งที่ build ต้องครอบผลการ resolve

**Reason:** ประโยคใน `model/v1` เขียนถึง *task schema* แต่ถูกอ่านเป็น *ทุกที่* — build artifact ที่บันทึกผลการ resolve คือ lockfile ไม่ใช่ hard-code และการห้ามมันจะทำให้ build ที่ทำซ้ำได้เป็นไปไม่ได้ · แต่การให้สิทธิ์นี้โดยไม่พูดว่า **identity ต้องครอบสิ่งที่ถูกแช่แข็ง** คือการรับรอง checksum ที่อ้างมากกว่าที่มันครอบ ซึ่งเป็น false ✅ ชนิดเดียวกับที่ ADR-0015 และ ADR-0016 เพิ่งปิดไป · ปฏิเสธ D เพราะตกเกณฑ์ ADR-0012 ที่ผู้ขอเองก็ประเมินตรงกัน

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### เงื่อนไขสามข้อที่ทำให้ binding ที่แช่แข็งไว้ถูกต้อง

```text
1. มาจากการ resolve capability requirement — ไม่ใช่คนพิมพ์ชื่อ model ลงไปเอง
2. requirement ยังเป็นแหล่งความจริง — binding คือ "ผลลัพธ์" ไม่ใช่ "คำประกาศ"
   ต้อง re-resolve ได้จาก requirement เดิมและอธิบายได้ว่าทำไมได้ตัวนี้
3. identity ของสิ่งที่ build ต้องครอบ binding นั้น
   → checksum ที่คำนวณจาก manifest อย่างเดียว บอกได้แค่ว่า manifest เหมือนกัน
     ไม่ได้บอกว่าสิ่งที่รันเหมือนกัน
```

ข้อ 3 คือข้อที่ทำให้ข้อ 1 กับ 2 ตรวจสอบได้ · **ถ้า identity ไม่ครอบ binding ก็ไม่มีทางรู้ว่าสองสิ่งที่ checksum เท่ากันรันด้วยอะไร** และคำว่า reproducible จะไม่มีความหมาย

### ใครเป็น authority ของ `ModelBinding` ที่ resolve แล้ว

**ไม่มีใคร — เพราะมันไม่ใช่การตัดสิน** · `capability_requirement` คือคำประกาศที่มีเจ้าของ (agent) ส่วน binding คือ **หลักฐานว่า ณ เวลานั้น catalog ตอบว่าอะไร**

หลักเดียวกับ [ADR-0016](0016-recording-which-consent-allowed-access.md) `$defs.Evaluation` — บันทึกผลที่แช่แข็งไว้ ไม่ใช่ตัวชี้ไปยังสิ่งที่จะถูกประเมินใหม่ · และเหตุผลที่ต้องแช่แข็งก็เหมือนกัน: **สิ่งที่ชี้ไปเปลี่ยนได้** (catalog เปลี่ยน model ถูก deprecate) ต่างจาก `approval_id` ใน [ADR-0019](0019-execution-records-its-approval.md) ที่ใบอนุมัติ immutable จึงเก็บ id ก็พอ

> เกณฑ์เดิมที่ ADR-0019 วางไว้ตอบข้อนี้ได้ทันที — **สิ่งที่ชี้ไปเปลี่ยนได้ไหม** · catalog เปลี่ยนได้ ⇒ ต้องแช่แข็งผล

### สิ่งที่เปลี่ยนในสัญญา

| ไฟล์ | เปลี่ยนอะไร |
| --- | --- |
| `model/v1` `Request.model_id` | แก้ถ้อยคำให้พูดถึง **task schema / request** ตามที่ตั้งใจ และระบุว่า build artifact ที่บันทึกผลการ resolve **ไม่ใช่การ hard-code** |
| `model/v1` `platform_rules` (ใหม่) | เงื่อนไขสามข้อข้างบน |

**ไม่นิยาม `CompiledAgent`** และไม่เพิ่ม field ให้มัน — รูปของ build artifact เป็นของ repo ที่ build

`model/v1` `v1.0.0` → **`v1.1.0`** · ไม่มี field เปลี่ยน ไม่มี `required` ขยับ · เป็นการเขียนความหมายที่ตั้งใจไว้แต่แรกให้ตรง

## Consequences

* `agent-builder-dsh-poc` เดินต่อได้ และรู้ว่าต้องแก้ `manifestChecksum` ให้ครอบ resolved binding ก่อนจะอ้าง portability
* consumer รายถัดไปที่อ่าน `model/v1` จะไม่สรุปว่า build-time binding ผิด
* **ผูกกับ [ADR-0022](0022-agent-may-narrow-its-own-scope.md)** — deny-list ของ agent ที่ถูก compile ลงไปก็อยู่ใต้เงื่อนไขข้อ 3 เดียวกัน · สองใบนี้ต้องอ่านคู่กันตามที่ผู้ขอตั้งข้อสังเกตไว้เอง
* **drift check ตรวจข้อนี้ไม่ได้** — identity ของ build artifact อยู่นอกสัญญา พิสูจน์ได้จากเทสของ repo ที่ build เท่านั้น
* ยังไม่ปิด และแยกเป็นใบของตัวเอง:
  * **`tool_calling` ไม่มีใน `CapabilityId`** ([#46](https://github.com/monthop-gmail/agent-platform/issues/46) ข้อ 2) — `model/v1` มี `tools` และ `ToolCall` แต่ taxonomy 13 ตัวไม่มีค่านี้ และ ADR-0009 บอกว่า *unknown = ไม่มี* ผู้ขอจึงแสดงข้อกำหนดนี้ไม่ได้เลย
  * **ย้าย provider กลางรอบต้องบันทึกไหม** ([#46](https://github.com/monthop-gmail/agent-platform/issues/46) ข้อ 1) — *"audit ที่บอกว่ารันด้วย model X ทั้งที่ครึ่งหลังรันด้วย Y คือบันทึกที่ไม่ตรง"* ถูกต้อง แต่เป็นเรื่องของ `event/v1` คนละ contract

## Sources

[issue #46](https://github.com/monthop-gmail/agent-platform/issues/46) · [ADR-0009](0009-capability-model.md) capability-first · `capability/v1` `constraints.pin_provider` · [ADR-0016](0016-recording-which-consent-allowed-access.md) เหตุผลที่บางอย่างต้องแช่แข็งผล · [ADR-0019](0019-execution-records-its-approval.md) เกณฑ์ *สิ่งที่ชี้ไปเปลี่ยนได้ไหม* · [ADR-0015](0015-event-sequence-and-trail-closure.md) กลไกที่อ้างมากกว่าที่ตัวเองครอบ
