# event/v1

## v1.1.0 — 2026-08-18
- **`EventType` เปลี่ยนจากชุดปิดเป็นชุดเปิด** — 7 ค่าเดิมเป็น *ขั้นต่ำที่ต้องมี* ไม่ใช่ชุดทั้งหมด
- **เพิ่ม event type ใหม่เป็น additive** ทำได้ผ่าน ADR ที่ repo นี้ ไม่ต้องมี RFC ที่ `devfactory-core`
  ตาม [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) ซึ่งแก้ Rule 2 ของ ADR-0006
- ลบ · เปลี่ยนชื่อ · เปลี่ยนความหมาย ของ 7 ค่าเดิม ยังเป็น semantic change เหมือนเดิม
- guarantee ทั้ง 8 ข้อไม่เปลี่ยน · ไม่มี field ใดเพิ่ม ลบ หรือเปลี่ยน type
- `derived_from.semantics_version` `1.0` → `1.1`
- **ไม่ breaking** — payload ที่ถูกต้องกับ v1.0.0 ยังถูกต้องกับ v1.1.0 ทุกตัว ชุดค่าที่ยอมรับกว้างขึ้นเท่านั้น

## v1.0.0 — 2026-08-18
- เขียนได้หลัง [`devfactory-core` RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) แยก authority เป็น semantics / wire schema
- semantics มาจาก `devfactory-core` `contract-semantics.yaml` `semantics_version: "1.0"` (RFC-0003 + RFC-0008)
- `job_id` optional · `subject_type` + `subject_id` required ตาม RFC-0008
- เพิ่ม field ระดับ platform: `tenant_id` `workspace_id` `correlation_id` `policy_result` `usage` `source` ตาม RFC-0005 Rule 1
- ตัดสินฝั่ง schema: **เก็บทั้ง `job_id` และ `subject_id`** เพราะเป็นคนละคำถาม (สายเหตุ vs หัวเรื่อง) พร้อมกฎว่าถ้า `subject_type: job` ต้องตรงกัน

## v1.1.0 — 2026-08-19

ไม่ breaking — ผ่อน validation และเพิ่มค่าใน enum เท่านั้น ([ADR-0006](../../../decisions/0006-contract-versioning.md))

- **`event_type` รับค่านอก 7 ตัวได้แล้ว** ([#17](https://github.com/monthop-gmail/agent-platform/issues/17)) — เพิ่ม `$defs.EventTypeName`
  (`type: string` + `pattern`) และให้ field อ้างตัวนั้นแทน `$defs.EventType`
  · `EventType` ยังอยู่เป็นชุดค่าที่ platform รับรองความหมาย ให้ consumer generate constant ได้
  · เดิม description เขียนว่าชุดเปิดแต่ `enum` ยังปิด ทำให้ขัดกับ `platform_rules` ในไฟล์เดียวกัน
    และขัดกับ ADR-0006 Rule 2 ฉบับแก้ (RFC-0009) · `devfactory-core` `payload_check` เจอตอนรันจริง
    (`SIGHTING_RECORDED` · `GEOFENCE_CROSSED` validate ไม่ผ่าน)
- **เพิ่ม `record` ใน `SubjectType`** ([#14](https://github.com/monthop-gmail/agent-platform/issues/14)) — บันทึกของโดเมนที่ต้องตามรอยได้แต่ไม่ได้เกิดจาก job
  · ชนิดจริงอยู่ใน `metadata.record_type` · แยกจาก `artifact` ที่เป็นผลผลิตของ execution
- semantics ไม่เปลี่ยน — vocabulary 7 ตัวและ guarantees ทั้ง 8 ข้อคงเดิม ไม่ต้องมี RFC ที่ต้นทาง
  (`semantics_version` ยัง `1.1`)
