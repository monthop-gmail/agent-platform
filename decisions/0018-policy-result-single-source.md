# ADR-0018: `event/v1.policy_result` — สำเนามือของ `Decision` ที่ไม่มีใครคอยจับว่าเพี้ยน

**Status:** Accepted (2026-08-21)
**Date:** 2026-08-21
**Depends on:** [ADR-0006](0006-contract-versioning.md) · [ADR-0010](0010-risk-approval-taxonomy.md) · [ADR-0016](0016-recording-which-consent-allowed-access.md)
**Blocking:** `contracts/event/v1` · `contracts/policy/v1`

## Context

[ADR-0016 ข้อค้นพบ 3](0016-recording-which-consent-allowed-access.md) บันทึกไว้ว่า `event/v1.policy_result` **ประกาศรูปของตัวเอง ไม่ได้ `$ref` ไปที่ `policy/v1` `Decision`**:

```yaml
# event/v1
policy_result:
  properties:
    effect:      { $ref: policy/v1#/$defs/Effect }       # ← ref แค่ "ค่า"
    authority:   { $ref: policy/v1#/$defs/Authority }
    action_risk: { $ref: capability/v1#/$defs/ActionRisk }
    policy_id:   { type: string }                        # ← โครงเป็นของตัวเอง
```

ผลคือมี **สองที่ที่ประกาศว่า "ผลของ policy หน้าตาอย่างไร"** และไม่มีอะไรคอยจับว่าทั้งสองยังตรงกัน — ADR-0016 เพิ่ง `consent` เข้า `Decision` ไป และมันไม่ไหลมาที่นี่เอง ต้องอาศัยคนจำ

นี่เป็น drift ชนิดเดียวกับที่ `drift_check` มีไว้จับข้าม repo — แต่เกิด **ภายในไฟล์ของเราเอง** ซึ่งไม่มี check ตัวไหนมอง

## ข้อเท็จจริงที่เปลี่ยนน้ำหนักของทางเลือก

**ไม่มี consumer รายไหนใช้ `policy_result` เลย** — ค้นทั้ง `devfactory-core` (0 ผลลัพธ์ทั้ง repo) และ `care-agent-platform` (GitHub code search = 0) ทั้งที่ทั้งคู่ pin `event/v1` และรัน payload จริงใน CI

แปลว่าการทำให้ field นี้เข้มขึ้น **ไม่ทำให้ payload ของใครพังวันนี้** · ตาม [ADR-0006](0006-contract-versioning.md) *"เข้มขึ้นใน validation"* ยังนับเป็น breaking ตามตัวอักษร — บันทึกไว้ตรง ๆ ว่าถ้าเลือกทางที่เข้มขึ้น เรากำลังใช้ **หลักฐานว่าไม่มีใครใช้** มาแทนที่กฎ ไม่ใช่ทำเป็นไม่เห็นกฎ

## แต่การยกทั้ง `Decision` มาใส่ event มีปัญหาของมันเอง

`Decision` มี `reason` ซึ่งเป็น **string อิสระ** · guarantee ข้อ 7 ของ `event/v1` (🔒 frozen เป็นของ `devfactory-core`):

> "ห้ามเก็บ private reasoning / chain-of-thought เป็น audit record"

`reason` ของ policy ไม่ใช่ chain-of-thought ของโมเดล จึงไม่ได้ละเมิดตรง ๆ — แต่การเปิดช่อง free text เข้าไปใน audit record โดยอัตโนมัติ **ผ่านการ `$ref` ไม่ใช่ผ่านการตัดสินใจ** คือวิธีที่ guarantee ข้อนี้จะถูกกัดกร่อนโดยไม่มีใครสังเกต

และ `expires_at` ของ `Decision` (*"decision ที่หมดอายุแล้วต้องประเมินใหม่"*) ไม่มีความหมายในบันทึกที่ immutable แล้ว

**สรุป: การที่ `policy_result` เป็นชุดย่อยเป็นเรื่องถูกต้อง ที่ผิดคือมันถูกประกาศซ้ำ ไม่ใช่ที่มันย่อ**

## Options

### A. `policy_result: { $ref: policy/v1#/Decision }` — ยกทั้งก้อน

* ✅ เหลือที่ประกาศเดียว · field ใหม่ใน `Decision` ไหลมาเองทันที
* ✅ ไม่มี payload ของใครพังวันนี้ (ไม่มีใครใช้)
* ❌ **ลาก `reason` เข้า audit record โดยอัตโนมัติ** — กัดกร่อน guarantee ข้อ 7 ผ่าน `$ref` แทนที่จะผ่านการตัดสินใจ
* ❌ `Decision.required` มี 4 ตัว → `policy_result` ที่ใส่ไม่ครบกลายเป็น invalid = เข้มขึ้น = breaking ตามตัวอักษรของ ADR-0006
* ❌ ทำให้ทุก field ที่ `policy/v1` เพิ่มในอนาคตกลายเป็นส่วนหนึ่งของ audit record โดยไม่มีใครเคาะ

### B. `policy/v1` นิยาม `$defs.DecisionSummary` แล้วให้ทั้งสองฝั่งอ้างตัวเดียวกัน ⭐

```yaml
# policy/v1
$defs:
  DecisionSummary:            # สี่ค่าที่ตอบว่า "ตัดสินว่าอะไร และตัดสินจากอะไร"
    properties: [effect, authority, action_risk, policy_id]

Decision:
  allOf: [ { $ref: '#/$defs/DecisionSummary' } ]
  required: [effect, authority, policy_id, evaluated_at]
  properties: [constraint, reason, evaluated_at, expires_at, consent]   # ส่วนที่เกิน

# event/v1
policy_result: { $ref: policy/v1#/$defs/DecisionSummary }
```

* ✅ **สี่ field ที่ใช้ร่วมกันถูกประกาศที่เดียว** — แก้ type หรือ `$ref` ของมันครั้งเดียวไหลไปทั้งสองที่
* ✅ **ชุดย่อยยังเป็นชุดย่อยโดยเจตนา** — field ใหม่ใน `Decision` *ไม่* ไหลเข้า audit เอง ต้องมีคนเคาะ ซึ่งเป็นสิ่งที่ควรเป็น
* ✅ **ไม่เข้มขึ้นเลย** — `DecisionSummary` ไม่มี `required` · payload เดิมทุกใบยัง valid · ไม่ breaking แม้ตามตัวอักษร
* ✅ `reason` และ `expires_at` อยู่นอก Summary จึงไม่มีทางหลุดเข้า event โดยอุบัติเหตุ
* ❌ เพิ่มชั้น `allOf` ใน `Decision` — อ้อมขึ้นหนึ่งชั้นเมื่ออ่านด้วยตา
* ❌ ยังต้องมีคนตัดสินตอน `Decision` ได้ field ใหม่ว่าจะเข้า Summary ไหม (แต่นั่นคือฟีเจอร์ ไม่ใช่บั๊ก)

### C. ปล่อยสำเนาไว้ แต่เพิ่ม check ที่จับว่าเพี้ยน

ให้ `drift_check` เทียบ property ที่ทับกันของ `policy_result` กับ `Decision` ว่า `$ref`/type ตรงกัน และให้ field ที่ตั้งใจไม่เอาต้องถูกประกาศไว้เป็นรายการ

* ✅ ไม่แตะ wire เลย
* ✅ ตรงกับนิสัยของ repo — จับด้วย check ไม่ใช่ด้วยความจำ
* ❌ **แก้อาการ ไม่แก้เหตุ** — ยังมีสองที่ที่ต้องแก้ให้ตรงกัน check แค่บอกว่าลืม
* ❌ เพิ่มโค้ดใน `conformance/` ซึ่ง [ADR-0011](0011-conformance-automation.md) บอกว่าถ้าเริ่มโตคือสัญญาณให้ทบทวน ไม่ใช่ให้ขยาย · และ B ทำให้ไม่มีอะไรเหลือให้ check เทียบ

### D. ลบ `policy_result` ทิ้ง — ให้ใช้ `event/v1` `metadata` แทน

* ❌ breaking ตรง ๆ · และทิ้งโครงสร้างที่ [ADR-0010](0010-risk-approval-taxonomy.md) ตั้งใจให้บันทึก `action_risk` กับ `authority` ที่ใช้ตัดสิน ไม่ใช่แค่ผลลัพธ์

### E. ไม่ทำอะไร — เขียนหมายเหตุว่าต้องแก้สองที่

* ✅ ศูนย์บาท · ไม่มีใครติดอยู่ตอนนี้
* ❌ ADR-0016 เพิ่งพิสูจน์ว่ามันเพี้ยนจริง (`consent` ไม่ไหลมา) · หมายเหตุไม่เคยหยุด drift ได้ มีแต่ทำให้คนที่มาทีหลังรู้ว่าเรารู้อยู่แล้วแต่ไม่ทำ

## Decision

**B** — `policy/v1` `$defs.DecisionSummary` ประกาศครั้งเดียว · `Decision` อ้างผ่าน `allOf` · `event/v1.policy_result` `$ref` ตัวเดียวกัน

**Reason:** ปัญหาคือ *ประกาศซ้ำ* ไม่ใช่ *ย่อ* — การที่ audit record เก็บชุดย่อยเป็นเรื่องถูกต้องและควรเป็นการตัดสินใจทุกครั้ง ไม่ใช่ผลข้างเคียงของ `$ref` (ปฏิเสธ A ซึ่งจะลาก `reason` ที่เป็น free text เข้า audit record โดยอัตโนมัติ เฉียดกับ guarantee ข้อ 7 ที่ frozen อยู่) · `DecisionSummary` ทำให้สี่ field ที่ใช้ร่วมกันมีที่ประกาศเดียวโดย **ไม่เข้มขึ้นแม้แต่นิดเดียว** จึงไม่ต้องพึ่งข้อเท็จจริงที่ว่าไม่มีใครใช้ field นี้มาแทนกฎของ ADR-0006 · ปฏิเสธ C เพราะแก้อาการไม่แก้เหตุ และหลัง B ก็ไม่เหลืออะไรให้ check เทียบอยู่ดี

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### ไม่ bump major

| contract | จาก | เป็น | เปลี่ยนอะไร |
| --- | --- | --- | --- |
| `policy/v1` | `v1.2.0` | `v1.3.0` | เพิ่ม `$defs.DecisionSummary` · `Decision` อ้างมันผ่าน `allOf` — **ชุด property และ `required` เท่าเดิมทุกตัว** |
| `event/v1` 🔗 | `v1.4.0` | `v1.5.0` | `policy_result` เปลี่ยนจากประกาศเองเป็น `$ref` — **รูปที่ยอมรับเหมือนเดิมเป๊ะ** |

ไม่มี field ถูกลบ เปลี่ยนชื่อ เปลี่ยน type · ไม่มี `required` ใหม่ · **ไม่มีการเข้มขึ้น** · payload ที่ valid กับเวอร์ชันก่อนหน้ายัง valid ทุกใบทั้งสองฝั่ง

`event/v1` `guarantees` ไม่ขยับ · `derived_from.semantics_version` ยัง `"1.1"`

## Consequences

* `policy/v1` `$defs.DecisionSummary` กลายเป็นคำตอบเดียวของ *"ผลของ policy ที่พอสำหรับ audit หน้าตาอย่างไร"*
* field ใหม่ใน `Decision` **จะไม่ไหลเข้า audit event เอง** — ต้องเคาะทุกครั้งว่าเข้า Summary ไหม · บันทึกกฎนี้ไว้ใน `policy/v1` เพื่อไม่ให้คนถัดไปคิดว่าเป็นความหลงลืม
* `consent` ที่ ADR-0016 เพิ่มเข้า `Decision` **จงใจไม่เข้า Summary** — `event/v1` มี `consent` ของตัวเองที่ระดับบนสุดแล้ว ใส่ซ้ำในสองที่ของ event เดียวกันคือ drift ที่รอเกิด
* ไม่มี consumer ต้องทำอะไร — ไม่มีใครใช้ `policy_result` และรูปที่ยอมรับไม่เปลี่ยน
* **drift check ไม่ต้องเพิ่ม check ใหม่** — โครงสร้างบังคับแทนแล้ว · `check_internal` ที่ตรวจ `$ref` resolve ครอบคลุมอยู่แล้วว่า `$ref` ใหม่ชี้ไปยังของที่มีจริง

## Sources

[ADR-0016](0016-recording-which-consent-allowed-access.md) ข้อค้นพบ 3 · [ADR-0010](0010-risk-approval-taxonomy.md) เหตุผลที่ `policy_result` ต้องเก็บ `action_risk` และ `authority` · `event/v1` guarantee ข้อ 7 (🔒 `devfactory-core` RFC-0003) · หลักฐานการใช้งาน: `grep -rn policy_result` ใน `devfactory-core` = 0 · GitHub code search ใน `care-agent-platform` = 0
