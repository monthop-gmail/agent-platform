# ADR-0020: event type ของ consent — กฎบังคับให้ออก event แต่ไม่มีชื่อให้ใช้

**Status:** Accepted (2026-08-21)
**Date:** 2026-08-21
**Depends on:** [ADR-0012](0012-consent-contract.md) · [ADR-0014](0014-consent-access-time-conditions.md) · [ADR-0016](0016-recording-which-consent-allowed-access.md) · [ADR-0006](0006-contract-versioning.md)
**Blocking:** `contracts/event/v1` · `care-agent-platform` ที่ต้องออก event พวกนี้อยู่ตอนนี้

## Context

`consent/v1` `consent_rules` ข้อ 2:

> "การให้ · การใช้ · และการเพิกถอน **ต้องออก audit event ทุกครั้ง** (`event/v1`)"

แต่ `EventType` — ชุดค่าที่ platform รับรองความหมาย — มี 7 ค่าและ **ไม่มีตัวไหนเกี่ยวกับ consent เลย**: `JOB_CREATED` `STATE_TRANSITION` `GOVERNANCE_DECISION` `TASK_ASSIGNED` `EXECUTION_STARTED` `EXECUTION_FAILED` `JOB_COMPLETED`

`event_type` เป็น**ชุดเปิด** ([RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md)) consumer จึงเติมชื่อเองได้และ validate ผ่าน — **นั่นแหละคือปัญหา**

```text
care-agent-platform ตั้ง  CONSENT_GRANTED
รายต่อไปตั้ง               GRANT_ISSUED
        ↓
สองชื่อสำหรับเหตุการณ์เดียวกัน · trail ข้าม consumer เชื่อกันไม่ได้
และไม่มีใครผิดเลยสักคน เพราะสัญญาไม่เคยตั้งชื่อให้
```

นี่เป็นแผลชนิดที่สี่ในตระกูลเดียวกัน — **กฎที่บังคับสิ่งที่สัญญาไม่ได้เตรียมไว้ให้** ([#22](https://github.com/monthop-gmail/agent-platform/issues/22) ไม่มี field · [ADR-0016](0016-recording-which-consent-allowed-access.md) ไม่มีที่บันทึกใบ · [ADR-0019](0019-execution-records-its-approval.md) ไม่มีที่ชี้ใบอนุมัติ · ครั้งนี้ไม่มี**ชื่อ**)

และเร่งด่วนกว่าสามครั้งก่อน เพราะ `care-agent-platform` **ต้องออก event พวกนี้ตั้งแต่ตอนนี้** — ยิ่งช้ายิ่งมีชื่อนอกสัญญาสะสมใน audit log ที่ append-only แก้ย้อนหลังไม่ได้

## อำนาจ — ทำได้เองแน่นอน

`contract-semantics.yaml` ของ `devfactory-core` เขียนไว้ตรง ๆ ใน `contracts.event.platform_may_add_freely`:

```yaml
- event type ใหม่
- subject_type / subject_id
```

และ `event_types.closed: false` · `EventType` ในไฟล์เราก็เขียนกำกับไว้แล้วว่า *"เพิ่ม event type ใหม่ = additive — `agent-platform` ทำได้เองผ่าน ADR ที่นี่ ไม่ต้องมี RFC ที่ต้นทาง"*

ต่างจาก `approval/v1` `Decision` ที่เป็นชุดปิด เพราะการเพิ่มค่าที่นั่นเปิดทางให้ execution เดินโดยไม่มี APPROVE ของคนได้ · **การเพิ่ม event type ไม่ทำแบบนั้น** — มันคือสิ่งที่สังเกตเพิ่ม ลดทอน guarantee ข้อใดไม่ได้

## คำถามที่ต้องเคาะจริง ๆ คือ "การใช้" ไม่ใช่ "การให้/เพิกถอน"

การให้และการเพิกถอนเป็น **การเปลี่ยนสถานะของตัวใบเอง** ซึ่งไม่มี event type ไหนครอบอยู่ — ต้องมีชื่อใหม่แน่นอน

แต่ **"การใช้"** ต่างออกไป — [ADR-0016](0016-recording-which-consent-allowed-access.md) เพิ่ง `consent` (`$defs.Evaluation`) เข้า `event/v1` ระดับบนสุดไปแล้ว แปลว่า **event ใดก็ได้พกผลการประเมินไปด้วยได้** · การอ่านข้อมูลผู้ป่วยที่ออก event ของโดเมนอยู่แล้ว เพียงแนบ `consent` เข้าไปก็บันทึกการใช้ครบตามกฎ

ถ้าเพิ่ม `CONSENT_USED` ขึ้นมาอีก จะเกิด **สองบันทึกของเหตุการณ์เดียวกัน** — event ของโดเมนที่มี `consent` กับ `CONSENT_USED` ที่ชี้ไปยังใบเดียวกัน แล้วไม่มีใครตอบได้ว่าอันไหนคือความจริง · เป็นปัญหาเดียวกับที่ [ADR-0018](0018-policy-result-single-source.md) เพิ่งเลิกทำ และเป็นหลักเดียวกับ *"สิ่งเดียวกันต้องเขียนได้แบบเดียว"* ที่ใช้กับ `expires_at: null` และ `conditions: []`

### แล้วการเข้าถึงที่ถูกปฏิเสธล่ะ

ครอบด้วยของที่มีอยู่แล้ว — `GOVERNANCE_DECISION` + `policy_result.effect: deny` + `consent.satisfied: false` ตอบได้ครบว่าใครถูกปฏิเสธ เพราะอะไร และใบไหนไม่ผ่าน

## Options

### A. `CONSENT_GRANTED` · `CONSENT_USED` · `CONSENT_REVOKED` — ตามตัวอักษรของกฎ 3 ข้อ

* ✅ อ่านกฎแล้วเจอชื่อครบทั้งสามคำ ไม่ต้องตีความ
* ✅ query *"ใบนี้ถูกใช้กี่ครั้ง"* ทำได้ด้วย `event_type` ตัวเดียว
* ❌ **สร้างสองบันทึกของการใช้ครั้งเดียวกัน** — event ของโดเมนที่พก `consent` กับ `CONSENT_USED` · อันไหนคือความจริง
* ❌ query ด้วย `event_type` จะ **ตกหล่นการใช้ที่ถูกบันทึกบน event ของโดเมน** — ซึ่งเป็นการใช้ส่วนใหญ่ · query ที่ถูกต้องคือหาจาก `consent.grant_id` ซึ่งครอบทั้งสองแบบอยู่แล้ว

### B. `CONSENT_GRANTED` · `CONSENT_REVOKED` + `SubjectType: consent` ⭐

การใช้บันทึกผ่าน `event/v1.consent` บน event ที่เกิดการเข้าถึงจริง ตามที่ ADR-0016 วางไว้

* ✅ **หนึ่งเหตุการณ์ หนึ่งบันทึก** — ไม่มีสองที่ที่พูดเรื่องเดียวกัน
* ✅ ครอบการใช้ที่เกิดบน event ของโดเมนด้วย ซึ่ง `CONSENT_USED` ครอบไม่ได้
* ✅ ตั้งชื่อให้เฉพาะสิ่งที่ยังไม่มีบ้าน — การเปลี่ยนสถานะของตัวใบ
* ❌ อ่านกฎข้อ 2 แล้วเห็นสามคำแต่มีสองชื่อ — **ต้องเขียนกำกับให้ชัด** ว่า "การใช้" บันทึกที่ไหน ไม่งั้นคนจะคิดว่าลืม

### C. B + `CONSENT_DENIED`

* ❌ `GOVERNANCE_DECISION` + `policy_result.effect: deny` + `consent.satisfied: false` ตอบครบอยู่แล้ว · เพิ่มมาก็เป็นชื่อที่สองของสิ่งเดิม

### D. ไม่ตั้งชื่อ — ปล่อยให้ consumer ตั้งเอง (สถานะปัจจุบัน)

* ✅ ยืดหยุ่นสูงสุด · ไม่ต้องตัดสินอะไร
* ❌ platform ถือ semantics ของ `consent/v1` เต็มตัว ([ADR-0012](0012-consent-contract.md) D1) แล้วไม่ตั้งชื่อให้เหตุการณ์ที่ตัวเองบังคับให้ออก — เป็นการโยนงานที่เป็นของตัวเอง
* ❌ ชื่อที่ต่างกันจะสะสมใน audit log ที่ **append-only** แก้ย้อนหลังไม่ได้

### E. ตั้งชื่อไว้ในเอกสาร แต่ไม่ใส่ใน `EventType` enum

* ✅ ไม่แตะ contract
* ❌ `EventType` มีไว้ *"ให้ consumer generate constant ของค่าที่ platform รับรองความหมาย"* ตามที่เขียนในไฟล์เอง — ชื่อที่ไม่อยู่ในนั้นคือชื่อที่ไม่ได้รับรอง

## Decision

**B** — `CONSENT_GRANTED` · `CONSENT_REVOKED` + `SubjectType: consent` · การใช้บันทึกด้วย field `consent` ไม่ใช่ event type แยก

**Reason:** ตั้งชื่อให้เฉพาะเหตุการณ์ที่ยังไม่มีบ้าน — การให้และการเพิกถอนเป็นการเปลี่ยนสถานะของตัวใบซึ่งไม่มี event type ไหนครอบ ส่วน**การใช้มีบ้านแล้ว**ตั้งแต่ ADR-0016 เพิ่ม `consent` เข้า `event/v1` ระดับบนสุด · การเพิ่ม `CONSENT_USED` จะสร้างบันทึกที่สองของเหตุการณ์เดียวกันและทำให้ query ด้วย `event_type` ตกหล่นการใช้ที่บันทึกบน event ของโดเมน ซึ่งเป็นส่วนใหญ่ · เพิ่ม `SubjectType: consent` ด้วยเพราะ consent เป็น contract ระดับ platform เหมือน `approval` ที่มีค่าของตัวเองอยู่แล้ว ไม่ใช่ record ของโดเมนที่ควรไปรวมใน `record`

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ต้องเขียนกำกับให้ชัดว่า "การใช้" อยู่ไหน

จุดอ่อนเดียวของ B คือคนอ่านกฎข้อ 2 จะเห็นสามคำแต่มีสองชื่อ แล้วคิดว่าลืม · แก้ด้วยการเขียนลง `consent_rules` ข้อนั้นตรง ๆ ว่าการใช้บันทึกด้วย `event/v1.consent` บน event ที่เกิดการเข้าถึงจริง ไม่ใช่ด้วย event type แยก

### ไม่ bump major — `event/v1` `v1.5.0` → `v1.6.0`

| เกณฑ์ breaking ของ [ADR-0006](0006-contract-versioning.md) | การเปลี่ยนนี้ |
| --- | --- |
| ลบค่าออกจาก enum · เปลี่ยนความหมายของค่าเดิม | ❌ 7 ค่าเดิมไม่ขยับ |
| เพิ่ม required · optional → required | ❌ ไม่มี |
| เข้มขึ้นใน validation | ❌ **ผ่อนอย่างเดียว** — `SubjectType` รับค่าเพิ่มหนึ่งค่า · `EventType` ไม่ได้ผูกกับ field อยู่แล้ว (field อ้าง `EventTypeName`) |

`guarantees` ไม่ขยับ · `derived_from.semantics_version` ยัง `"1.1"` เพราะ `event_types.closed: false` และทั้งสองอย่างอยู่ใน `platform_may_add_freely`

## Consequences

* `care-agent-platform` มีชื่อกลางใช้ทันที — ถ้าเขาตั้งชื่ออื่นไปแล้วคือ rename ไม่ใช่ออกแบบใหม่ (รูปแบบเดียวกับ [#22](https://github.com/monthop-gmail/agent-platform/issues/22))
* `consent_rules` ข้อ 2 ขยายความให้ระบุว่าการใช้บันทึกที่ไหน — กฎเดิมไม่ถูกลดทอน แค่บอกวิธีทำตาม
* `devfactory-core` **ไม่กระทบ** — ไม่ pin `consent/v1` และค่าที่เพิ่มเป็น additive ล้วน
* **drift check ไม่ต้องแก้** — `check_frozen` เทียบกับ `required_minimum` ของต้นทางซึ่ง `closed: false` ค่าที่เกินจึงไม่ FAIL · `check_binding` ก็ยังถูกเพราะ field ยังผูกกับ `EventTypeName` ไม่ใช่ enum
* ยังไม่ปิด: 16 จาก 20 ไฟล์ schema ไม่มี `guarantees`/`platform_rules` เลย · และคำถามว่า **การไล่ guarantee เทียบ properties ควรเป็นงานประจำไหม** ซึ่งตอนนี้เจอของจริงไปแล้ว 4 ครั้ง

## Sources

`consent/v1` `consent_rules` ข้อ 2 · [`contract-semantics.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/contract-semantics.yaml) `contracts.event.platform_may_add_freely` (*"event type ใหม่"* · *"subject_type / subject_id"*) · [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) · [ADR-0016](0016-recording-which-consent-allowed-access.md) ที่ทำให้ event ใดก็พก `consent` ได้ · [ADR-0018](0018-policy-result-single-source.md) สำเนาที่ซ้ำได้คือสำเนาที่ drift ได้ · [#14](https://github.com/monthop-gmail/agent-platform/issues/14) ที่เพิ่ม `record` เข้า `SubjectType`
