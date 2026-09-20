# approval/v1

## v1.3.0 — 2026-09-20

`derived_from.semantics_version` `1.2` → `1.5` · **สองรอบที่ข้ามมาแตะใบนี้ทั้งคู่ ต่างจาก `v1.2.1` และ `v1.2.2` ที่ขยับ pointer เฉย ๆ** ([ADR-0034](../../../decisions/0034-semantics-1-5-leaf-declaration.md))

### `1.4` — `subject.type` เป็นชุดเปิด และได้ค่า `record`

ปิด [#73](https://github.com/monthop-gmail/agent-platform/issues/73) · [RFC-0016](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0016-approval-subject-types.md)

ห้าค่าเดิมเป็นของ **ระบบที่รัน agent** ทั้งหมด ไม่มีค่าสำหรับ **บันทึกของโดเมน** · `care-agent-platform` เลือก `artifact` ให้คำสั่งหมอที่รอมีผล และ `tool_call` ให้คำขอลบข้อมูลตาม PDPA — **ทั้งคู่ validate ผ่าน และ audit event ของวัตถุเดียวกันใช้ `subject_type: record` อยู่แล้ว**

> วันนี้ระบบเดียวกันอธิบายสิ่งเดียวกันด้วยคำสองคำ ขึ้นกับว่ากำลังเขียนลง `event/v1` หรือ `approval/v1`

* `$defs.SubjectType` — 🔓 ชุดเปิด 6 ค่า · **ยืมนิยาม `record` จาก `event/v1` ทั้งดุ้น ไม่เขียนใหม่**
* `$defs.SubjectTypeName` — pattern ที่ field อ้างจริง · รูปเดียวกับ `EventType` / `EventTypeName`
* 🔒 **เจ้าของคนละคนกับ `event/v1` `SubjectType` ที่ชื่อเหมือนกัน** — ของ `event` อยู่ใน `platform_may_add_freely` คือ enum เป็นของเรา · ของที่นี่เป็น semantics ของต้นทาง เพิ่มค่าต้องมี RFC

### `1.5` — `reason` เป็น leaf ที่ประกาศแล้ว

[RFC-0017](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0017-the-leaf-rule-is-not-a-property-of-one-contract.md) ตอบคำถามที่เราถามไว้ที่ [`devfactory-core#46`](https://github.com/monthop-gmail/devfactory-core/issues/46) ว่ากฎ leaf ผูกใบนี้ด้วยหรือไม่ — **ผูก** เพราะ *"กฎนี้เป็นคุณสมบัติของข้อความที่ลบไม่ได้เมื่อเขียนลงไปแล้ว ไม่ใช่คุณสมบัติของ `event/v1`"*

ข้อที่เราฝากให้คิดคู่กันแล้วเขาชี้ว่ากลับทาง: `required` + `minLength: 1` **เป็นเหตุผลให้มีกฎ ไม่ใช่เหตุผลไม่ให้มี** — `transition.reason` optional ผู้ผลิตเลิกส่งได้ · ที่นี่ไม่มีทางออกนั้น **สิ่งเดียวที่เปลี่ยนได้ตลอดอายุของมันคือคำตอบเรื่องชั้นของกฎการเก็บ**

### ไม่ breaking

`subject.type` **กว้างขึ้น ไม่ได้แคบลง** · `reason` ไม่แตะ `type` ไม่แตะ `required` ไม่แตะ `minLength` · payload ที่ valid กับ `v1.2.2` ยัง valid ทุกใบ

## v1.2.2 — 2026-09-17

`derived_from.semantics_version` `1.2` → `1.3` ตามต้นทาง · **สัญญาไม่ขยับ**

RFC-0013 เพิ่ม invariant ให้ `event` · `approval` ขยับเพราะ `semantics_version` เป็นของ manifest ทั้งไฟล์ ไม่ได้แยกต่อ contract — เหมือนรอบ 1.2

⚠️ แต่รอบนี้มีของที่เกี่ยวจริง: `reason` ของ `approval/v1` มี `minLength: 1` และ**เป็น leaf ที่ถือข้อความของคนตามนิยามของ RFC-0013** · ผู้ผลิต `devfactory-core` ประกาศ `metadata.approval.reason` ไว้ใน manifest ของตัวเองแล้ว · ถ้า ADR ที่จะเขียนถึง `transition.reason` ควรพิจารณา `approval/v1.reason` พร้อมกัน

## v1.2.1 — 2026-08-21

`derived_from.semantics_version` `1.1` → `1.2` ตามต้นทาง · **สัญญาไม่ขยับแม้แต่ตัวอักษรเดียว**

RFC-0012 แตะเฉพาะ guarantee ของ `event` · pointer ต้องขยับเพราะ `semantics_version` เป็นของ manifest ทั้งไฟล์ ไม่ได้แยกต่อ contract — ถ้าอยากให้ contract ที่ไม่เกี่ยวไม่ต้องขยับตาม ต้องแยก version ต่อ contract ที่ต้นทาง ซึ่งเป็นการเปลี่ยนกลไก ไม่ใช่การแก้รอบนี้

## v1.2.0 — 2026-08-21

* `correlation_id` (optional) — ผูกใบอนุมัติเข้ากับสายงานเดียวกันข้าม service ([ADR-0019](../../../decisions/0019-execution-records-its-approval.md))

contract อื่นเกือบทั้งหมดมี field นี้ (`event/v1` · `identity/v1` `RequestContext` ที่ `execution/v1` ใช้ผ่าน `context`) แต่ไฟล์นี้ไม่มี — `execution_id` กับ `subject` ทำแทนไม่ได้ เพราะการอนุมัติหนึ่งครั้งอาจเกิดก่อน execution ถูกสร้าง หรือครอบหลาย execution ในสายเดียวกัน

เป็น **field ระดับ platform** ตาม [ADR-0006 กฎข้อ 1](../../../decisions/0006-contract-versioning.md) — เพิ่มได้เองโดยไม่ต้องมี RFC ที่ `devfactory-core`

**`guarantees` ไม่ขยับ** (ยัง 4 ข้อ) · `derived_from.semantics_version` ยัง `"1.1"` · optional · `required` ยัง 7 ตัวเท่าเดิม

## v1.1.0 — 2026-08-19

ไม่ breaking — เพิ่ม optional field อย่างเดียว ([ADR-0006](../../../decisions/0006-contract-versioning.md) · [ADR-0013](../../../decisions/0013-approval-supersedes-chain.md))

- **เพิ่ม `supersedes_approval_id`** ([#22](https://github.com/monthop-gmail/agent-platform/issues/22)) — approval ใบที่ใบนี้มาแทน
  · `$ref` ไปที่ `identity/v1#/$defs/Id` เหมือน `approval_id` ที่มันชี้ไป
- ปิดช่องว่างที่ guarantee ข้อแรกบังคับให้ *"การเปลี่ยนใจคือ approval ใบใหม่ที่อ้างใบเดิม"*
  แต่ `properties` **ไม่มี field ไหนอ้างใบเดิมได้เลย** — consumer ทำตาม guarantee แล้วห่วงโซ่ยังขาดใน audit trail
- **optional โดยเจตนา** — ใบแรกของเรื่องหนึ่งไม่มีใบให้อ้าง · การบังคับอยู่ที่ description
  (*ต้องมีเมื่อเป็นการเปลี่ยนใจ*) ไม่ใช่ที่ `required` · ไม่มี field นี้ = **อ้างว่าเป็นใบแรก** ไม่ใช่ *ไม่ระบุ*
- semantics ไม่เปลี่ยน — `$defs.Decision` ยัง 3 ค่า · guarantees ทั้ง 4 ข้อคงเดิมทุกตัวอักษร
  · เป็น field ระดับ platform ตาม [ADR-0006 กฎข้อ 1](../../../decisions/0006-contract-versioning.md)
  และ `platform_may_add_freely` ของต้นทาง จึงไม่ต้องมี RFC ที่ `devfactory-core` (`semantics_version` ยัง `1.1`)
- payload ที่ valid กับ v1.0.1 **ยัง valid ทุกใบ** · `required` ไม่ขยับ (7 ตัวเท่าเดิม)

## v1.0.1 — 2026-08-18
- `derived_from.semantics_version` `1.0` → `1.1` ตามต้นทางที่ขยับจาก [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md)
- **`$defs.Decision` ยังเป็นชุดปิดเหมือนเดิม — ไม่มีอะไรเปลี่ยนในสัญญา** RFC-0009 เปิดเฉพาะ `event/v1` `EventType`
- เพิ่มคำอธิบายว่าทำไมที่นี่ต่างจาก `event/v1`: การเพิ่ม decision outcome เปิดทางให้ execution
  เดินโดยไม่มี `APPROVE` ของคนได้ ส่วนการเพิ่ม event type ทำแบบนั้นไม่ได้
- แก้เฉพาะ description และ pointer — schema ไม่ขยับ

## v1.0.0 — 2026-08-18
- เขียนได้หลัง [`devfactory-core` RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) แยก authority เป็น semantics / wire schema — ไม่ติด `external-authority-pending` อีกต่อไป
- semantics มาจาก `devfactory-core` `contract-semantics.yaml` `semantics_version: "1.0"`
- field ระดับ platform (`tenant_id` `workspace_id` `execution_id` `agent_id` `policy_id` `expires_at` `action_risk` `escalation_target`) เพิ่มได้ผ่าน ADR ฝั่งนี้อย่างเดียวตาม RFC-0005 Rule 1
