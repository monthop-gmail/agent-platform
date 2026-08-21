# ADR-0016: บันทึกว่า "อนุญาตด้วยความยินยอมใบไหน" — ช่องว่างของด่านที่สอง

**Status:** Accepted (2026-08-21)
**Date:** 2026-08-21
**Depends on:** [ADR-0012](0012-consent-contract.md) · [ADR-0014](0014-consent-access-time-conditions.md) · [ADR-0010](0010-risk-approval-taxonomy.md) · [ADR-0006](0006-contract-versioning.md)
**Blocking:** `contracts/policy/v1` · `contracts/consent/v1` · `contracts/event/v1` · รายการที่ค้างไว้ใน [`consent/v1` CHANGELOG v1.0.0](../contracts/consent/v1/CHANGELOG.md)

## Context

`consent/v1` `consent_rules` ข้อ 6 บังคับไว้ว่า:

> "การเข้าถึงต้องผ่านทั้ง `policy/v1` และ consent — ผ่านด่านเดียวไม่พอ"

แต่ไล่ `Decision` ของ `policy/v1` ครบทุก field — `effect` `authority` `constraint` `action_risk` `policy_id` `reason` `evaluated_at` `expires_at` — **ไม่มีที่บันทึกว่าอนุญาตโดยอาศัยความยินยอมใบไหน**

```text
กฎบังคับ:   ต้องผ่านสองด่าน
record ให้:  ผลของด่านเดียว
        ↓
audit ตอบได้ว่า "อนุญาต" แต่ตอบไม่ได้ว่า "ด้วยความยินยอมของใคร ใบไหน"
```

เป็นความล้มเหลวชนิดเดียวกับ [#22](https://github.com/monthop-gmail/agent-platform/issues/22) — **กฎที่บังคับสิ่งที่ schema ไม่มีที่ให้ทำตาม** · ต่างกันที่ครั้งนั้นเจอเพราะมีคน implement ครั้งนี้เจอตอนไล่ของค้างในแผน

รายการนี้ถูกเขียนค้างไว้ตั้งแต่ [`consent/v1` v1.0.0](../contracts/consent/v1/CHANGELOG.md) ว่า *"`policy/v1` `Decision` เพิ่ม optional `consent_id` — แยกเป็นการเปลี่ยนอีกครั้ง เพื่อให้ `consent/v1` ยืนได้เองก่อน"* · ตอนนี้ `consent/v1` ยืนได้แล้วและมี consumer ใช้จริง จึงถึงคิว — **แต่รูปที่เขียนค้างไว้ตอนนั้นไม่ถูกอีกต่อไป**

`Decision.action_risk` วางบรรทัดฐานไว้แล้วว่า record ของด่านต้องเก็บ *สิ่งที่ใช้ตัดสิน* ไม่ใช่แค่ผลลัพธ์:

> "ค่าที่ใช้ประกอบการตัดสิน — บันทึกไว้ด้วยเพื่อให้ audit ย้อนหลังรู้ว่าตัดสินจากอะไร ไม่ใช่แค่ผลลัพธ์"

## ข้อค้นพบ 1 — `consent_id` เปล่า ๆ ปิดช่องไม่ได้

[ADR-0014](0014-consent-access-time-conditions.md) เปลี่ยนธรรมชาติของ `consent/v1` ไปแล้ว: ใบที่มี `conditions` **ตอบตัวเองไม่ได้** ความถูกต้องขึ้นกับสถานะที่อยู่นอก payload

ผลคือการรู้แค่ `grant_id` ตอบคำถาม audit ไม่ได้:

```text
ปีหน้า auditor ถาม:  "ตอนนั้นเข้าถึงได้โดยชอบไหม"
มีแค่ grant_id  →    ไปอ่านใบนั้น → ใบยังไม่ถูกเพิกถอน ยังไม่หมดอายุ
                     → แต่ conditions ต้องประเมิน "ตอนเข้าถึง" ซึ่งผ่านไปแล้ว
                     → ประเมินใหม่วันนี้ = คำตอบของวันนี้ ไม่ใช่ของวันนั้น
```

หมอที่ลาออกไปแล้ววันนี้จะทำให้ replay สรุปว่า *"การเข้าถึงเมื่อปีที่แล้วไม่ชอบ"* ทั้งที่ตอนนั้นเขายังสังกัดอยู่ — **ผิดอย่างมั่นใจ** และผิดในทางที่กล่าวหาคนที่ทำถูก

`consent_id` เดี่ยว ๆ จึงเป็นความผิดพลาดแบบเดียวกับ [ADR-0015](0015-event-sequence-and-trail-closure.md): **กลไกที่ดูเหมือนตอบคำถาม แต่ตอบคำถามที่แคบกว่า** · สิ่งที่ต้องถูกแช่แข็งไว้ในบันทึกคือ **ผลการประเมิน ณ วินาทีนั้น** ไม่ใช่ตัวชี้ไปยังใบที่จะถูกประเมินใหม่

## ข้อค้นพบ 2 — `policy/v1` ไม่ได้เป็นคนประเมิน consent

`Request` ของ `policy/v1` มี `context` · `subject` (ผู้กระทำ) · `action` — **ไม่มี field ไหนบอกว่าเป็นข้อมูลของใคร** · `action.resource` เป็น string อิสระ

แปลว่าวันนี้ policy engine **ไม่มีทางรู้จักด่านที่สองเลย** — สองด่านถูก AND กันโดยผู้เรียก ไม่ใช่โดย policy

การเขียน `consent_id` ลงใน `Decision` เฉย ๆ จึงเป็นการ **บันทึกสิ่งที่ผู้ตัดสินไม่เคยเห็น** — record จะอ่านได้ว่า policy พิจารณาความยินยอมแล้ว ทั้งที่ไม่เคยได้รับมา · ทางที่ซื่อสัตย์มีสองทางเท่านั้น: **ส่งให้ policy เป็น input จริง ๆ** หรือ **บันทึกไว้ที่ record ของการเข้าถึง ไม่ใช่ที่ record ของ policy**

## ข้อค้นพบ 3 — `event/v1.policy_result` เป็นสำเนามือของ `Decision`

`policy_result` ประกาศ `effect` `authority` `action_risk` `policy_id` ซ้ำเอง **ไม่ได้ `$ref` ไปที่ `Decision`** · field ที่เพิ่มใน `Decision` จึงไม่ไหลไปถึง audit event เอง ต้องเพิ่มสองที่และจำให้ได้ว่าต้องเพิ่ม

บันทึกไว้ที่นี่เพราะเป็น drift ที่รอเกิด — **แต่ไม่แก้ใน ADR นี้** เพราะเป็นคนละเรื่องและควรมี ADR ของตัวเอง

## ข้อค้นพบ 4 — คำว่า `subject` แปลว่าคนละอย่างใน 3 contract

| contract | `subject` คือ |
| --- | --- |
| `policy/v1` `Request.subject` | **ผู้กระทำ** — *"ใครจะทำ"* |
| `consent/v1` `subject_id` | **เจ้าของข้อมูล** — เขียนกำกับไว้เองว่า 🔒 *"ไม่ใช่ actor และไม่ใช่ resource"* |
| `event/v1` `subject_type`/`subject_id` | **หัวเรื่องของบันทึก** — job · execution · step · agent · tool_call · artifact · approval · external · record |

สองอันแรก**ขัดกันตรง ๆ** และคำนี้ **ไม่อยู่ในตารางศัพท์ที่ lock ไว้** ของ [`decisions/README.md`](README.md)

เรื่องนี้จะกัดคนที่กำลังจะมาต่อ ไม่ใช่คนที่ต่ออยู่แล้ว — `enterprise-knowledge` กำลังจะ map `Principal` / `TenantScope` / `PolicyContext` ของเขาเข้ากับ contract ชุดนี้ ([#17 ของเขา](https://github.com/monthop-gmail/enterprise-knowledge/issues/17)) และคนที่อ่าน `policy/v1` กับ `consent/v1` เรียงกันจะเข้าใจ `subject` สลับกันได้ทันที ซึ่งในบริบทนี้แปลว่า **เอาข้อมูลของคนหนึ่งไปตอบสิทธิ์ของอีกคน**

**ไม่แก้ใน ADR นี้** — เสนอเป็น ADR-0017 แยก เพราะแตะทั้ง vocabulary lock และหลาย contract · แต่ต้องรีบ เพราะมี consumer รายใหม่กำลังอ่านอยู่ตอนนี้

## Options

### A. `Decision.consent_id` optional — ตามที่เขียนค้างไว้ใน v1.0.0

* ✅ เล็กที่สุด · ทำใน contract เดียว
* ❌ **ไม่ปิดช่อง audit** — id ชี้ไปยังใบที่ต้องประเมินใหม่ ซึ่งให้คำตอบของวันนี้ไม่ใช่ของวันนั้น (ข้อค้นพบ 1)
* ❌ **บันทึกสิ่งที่ policy ไม่เคยเห็น** (ข้อค้นพบ 2)
* ❌ ไม่ไหลไปถึง `event/v1` เอง (ข้อค้นพบ 3)

### B. `Request.consent_id` + `Decision.consent_id`

* ✅ ซื่อสัตย์ขึ้น — policy ได้รับ id มาจริง
* ❌ ยังเป็น id ไม่ใช่ผลการประเมิน — ข้อค้นพบ 1 ยังอยู่ครบ

### C. นิยาม `consent/v1` `$defs.Evaluation` ครั้งเดียว แล้วให้ contract อื่น `$ref` ⭐

```yaml
# consent/v1
Evaluation:
  required: [grant_id, evaluated_at, satisfied]
  properties:
    grant_id:            # ใบที่ใช้
    evaluated_at:        # ประเมินเมื่อไร — เวลาที่แช่แข็งคำตอบไว้
    satisfied:           # ผลตอนนั้น (บันทึกทั้งผ่านและไม่ผ่าน)
    conditions_checked:  # kind ที่ถูกตรวจ — ว่างได้ถ้าใบไม่มีเงื่อนไข
```

* `policy/v1` `Request.consent` (optional input) + `Decision.consent` (echo เมื่อได้รับมา)
* `event/v1` `consent` (optional) — บ้านของ audit ที่แท้จริง

* ✅ **แช่แข็งคำตอบไว้ที่วินาทีที่ประเมิน** — replay ปีหน้าอ่านผลของวันนั้น ไม่ใช่ประเมินใหม่ด้วยข้อเท็จจริงของวันนี้
* ✅ นิยามอยู่ที่เดียว — `consent/v1` ที่ platform ถือ semantics เองทั้งหมด **ไม่มีข้อพิพาท authority** และไม่ต้องรอ RFC ที่ repo ไหน
* ✅ policy จะ *ใช้* consent ประกอบการตัดสินก็ได้ (เช่นกฎ "ไม่มีใบ = deny") หรือจะไม่ใช้ก็ได้ — record ไม่โกหกทั้งสองทาง
* ✅ ปิดของค้างอีกข้อไปพร้อมกัน — *"`event/v1` บันทึกว่าเงื่อนไขถูกประเมินแล้วและผ่าน"* ที่ [ADR-0014](0014-consent-access-time-conditions.md) ฝากไว้
* ❌ แตะ 3 contract ในรอบเดียว (แต่เป็น **นิยามเดียว + สอง `$ref`** ไม่ใช่สามนิยาม)
* ❌ `satisfied: false` ทำให้เก็บ record ของการเข้าถึงที่ถูกปฏิเสธด้วย — ตั้งใจ แต่ consumer ต้องรู้ว่าไม่ใช่ทุก record คือการอนุญาต

### D. บันทึกที่ `event/v1` อย่างเดียว ไม่แตะ `policy/v1`

* ✅ ตรงที่สุดกับข้อค้นพบ 2 — audit อยู่ที่ event ไม่ใช่ที่ decision
* ✅ เล็กกว่า C หนึ่งชั้น
* ❌ ปิดประตูไม่ให้ policy ใช้ consent ประกอบการตัดสินได้เลย — ซึ่ง `enterprise-knowledge` ต้องการพอดี (ACL-aware retrieval คือการถามว่า *คนนี้เห็นเอกสารของใครได้*)
* ❌ ของค้างในแผนที่เขียนว่า `policy/v1` จะยังค้างต่อไปโดยไม่มีคำตอบว่าตกลงทำหรือไม่ทำ

### E. ไม่ทำ — ให้ consumer join ด้วย `correlation_id`

* ✅ ไม่ต้องแก้ contract · `event/v1` มี `correlation_id` อยู่แล้ว
* ❌ ต้องมี event ทั้งสองฝั่งอยู่ครบและถูกเก็บนานเท่ากัน — ถ้าฝั่งใดหาย คำตอบหายเงียบ ๆ
* ❌ ไม่บอกว่าใช้ใบไหน เมื่อมีหลายใบที่เข้าเกณฑ์พร้อมกัน
* ❌ ยังไม่แช่แข็งผลการประเมิน — ข้อค้นพบ 1 ไม่ถูกแตะเลย

### F. ให้ `policy/v1` ประเมิน consent เอง — รวมสองด่านเป็นด่านเดียว

* ✅ ผู้เรียกเหลือด่านเดียวให้เรียกผิด
* ❌ ขัด [ADR-0012](0012-consent-contract.md) โดยตรง — policy เป็นกฎของ **ผู้ควบคุมข้อมูล** ส่วน consent เป็นสิ่งที่ **เจ้าของข้อมูล** ให้ · รวมกันแล้วการแก้ policy จะขยายสิ่งที่ *ดูเหมือน* เจ้าของยินยอมได้เงียบ ๆ ซึ่งเป็นเหตุผลที่ contract นี้ถูกแยกออกมาแต่แรก
* ❌ ทำให้ audit แยกไม่ออกว่า "เข้าไม่ได้เพราะเจ้าของไม่ยอม" กับ "เข้าไม่ได้เพราะกฎองค์กร"

## Decision

**C** — นิยาม `consent/v1` `$defs.Evaluation` ครั้งเดียว แล้วให้ `policy/v1` (`Request` + `Decision`) และ `event/v1` `$ref` ตัวเดียวกัน

**Reason:** ของที่เขียนค้างไว้ใน v1.0.0 (option A) **ไม่ถูกอีกต่อไปหลัง ADR-0014** — ตัวชี้ไปยังใบที่ต้องประเมินใหม่ให้คำตอบของวันนี้ ไม่ใช่ของวันที่เข้าถึง และ replay จะกล่าวหาคนที่ทำถูกอย่างมั่นใจ · สิ่งที่ต้องเก็บคือ **ผลการประเมินที่ถูกแช่แข็ง** ไม่ใช่ id · วางนิยามไว้ที่ `consent/v1` เพราะ platform ถือ semantics เองทั้งหมด ทำได้ทันทีโดยไม่ต้องรอ RFC ที่ repo ไหน แล้วให้ `policy/v1` กับ `event/v1` `$ref` ตัวเดียวกัน — **หนึ่งนิยาม สองที่ใช้** ไม่ใช่สามนิยามที่ต้อง drift ตามกันภายหลัง · ปฏิเสธ D เพราะปิดประตูที่ `enterprise-knowledge` กำลังจะเดินเข้าพอดี · ปฏิเสธ F เพราะรวมสองด่านคือการยกกฎของผู้ควบคุมข้อมูลขึ้นมาแทนความยินยอมของเจ้าของข้อมูล

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ไม่ bump major ทั้งสามตัว

ทุกการเปลี่ยนเป็น **optional field ใหม่** ล้วน — `required` ของทั้งสาม contract ไม่ขยับ · payload เดิม valid ทุกใบ

| contract | จาก | เป็น |
| --- | --- | --- |
| `consent/v1` | `v1.1.0` | `v1.2.0` — `$defs.Evaluation` |
| `policy/v1` | `v1.0.0` | `v1.1.0` — `Request.consent` · `Decision.consent` |
| `event/v1` 🔗 | `v1.3.0` | `v1.4.0` — `consent` |

`event/v1` เป็น derived contract แต่ **`guarantees` ไม่ขยับ** และ field ระดับ platform เพิ่มได้เองตาม [ADR-0006 กฎข้อ 1](0006-contract-versioning.md) · `derived_from.semantics_version` ยัง `"1.1"`

## Consequences

* `care-agent-platform` ได้ที่บันทึกว่า **หมอคนนั้นเข้าถึงด้วยใบไหน และตอนนั้นเงื่อนไขผ่าน** — ปิดช่อง replay ที่ ADR-0014 เปิดค้างไว้ ครึ่งที่เป็นของเรา
* `enterprise-knowledge` ที่กำลังทำ ACL-aware retrieval มีทางส่ง consent เข้า policy เป็น input แทนที่จะต้องคิดรูปเอง — ตอบ [#17 ของเขา](https://github.com/monthop-gmail/enterprise-knowledge/issues/17) ได้ด้วยของที่มีจริง
* `devfactory-core` **ไม่ได้รับผลกระทบ** — ไม่ pin `consent/v1` และ field ใหม่เป็น optional ทั้งหมด
* ปิดของค้าง 2 ใน 4 ข้อในแผน (`policy/v1` `consent_id` · `event/v1` บันทึกการประเมินเงื่อนไข) โดยไม่ต้องรอใคร
* **drift check ตรวจข้อนี้ไม่ได้** — ตรวจได้แค่ว่า schema valid และ `$ref` resolve · กฎว่า "ต้องบันทึกตอนเข้าถึง" พิสูจน์ได้จาก payload จริงของ consumer เท่านั้น ตามขอบเขต [ADR-0011](0011-conformance-automation.md)
* ค้างไว้ต่อ: `event/v1.policy_result` ที่เป็นสำเนามือของ `Decision` (ข้อค้นพบ 3) · และคำว่า `subject` ที่แปลว่าคนละอย่างใน 3 contract (ข้อค้นพบ 4) — **ข้อหลังควรทำก่อน** เพราะมี consumer รายใหม่กำลังอ่านอยู่

## Sources

[`consent/v1` CHANGELOG v1.0.0](../contracts/consent/v1/CHANGELOG.md) "ยังไม่ทำในรอบนี้" · [ADR-0014](0014-consent-access-time-conditions.md) ช่องว่าง audit ย้อนหลัง · [ADR-0015](0015-event-sequence-and-trail-closure.md) บทเรียนกลไกที่ตอบคำถามแคบกว่า · [ADR-0013](0013-approval-supersedes-chain.md) กฎที่ schema ไม่มีที่ให้ทำตาม · [enterprise-knowledge#17](https://github.com/monthop-gmail/enterprise-knowledge/issues/17)
