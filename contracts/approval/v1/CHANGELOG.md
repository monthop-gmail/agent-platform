# approval/v1

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
