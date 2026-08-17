# contracts/event — ⏳ `external-authority-pending`

**ยังไม่เขียน schema** ด้วยเหตุผลเดียวกับ [`contracts/approval/`](../approval/README.md)

## ทำไม

contract นี้จะมาจาก [`devfactory-core/rfcs/0003-audit-event-log-schema.md`](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0003-audit-event-log-schema.md) ซึ่งยัง `Draft` และ authority ยังอยู่ที่ repo นั้น — ดู [ADR-0006](../../decisions/0006-contract-versioning.md) และ [issue #6](https://github.com/monthop-gmail/agent-platform/issues/6)

## สิ่งที่จะอยู่ในนี้เมื่อได้รับการยืนยัน

จาก RFC-0003 (ใช้ semantics ได้เลย):

```text
JOB_CREATED · STATE_TRANSITION · GOVERNANCE_DECISION · TASK_ASSIGNED
EXECUTION_STARTED · EXECUTION_FAILED · JOB_COMPLETED

guarantees: append-only · no silent state change
```

ที่ต้องแก้/เพิ่มก่อนใช้ระดับ platform:

| ประเด็น | สิ่งที่ต้องทำ |
| --- | --- |
| `job_id` เป็น required | ทำเป็น optional + เพิ่ม `subject_id`/`subject_type` เพราะ event จาก `navi-ims` (sighting, geofence) ไม่ได้เกิดจาก job |
| field มีแค่ 5 ตัว | ขยายเป็นชุดของ `backend-os §14` 13 ตัว + `tenant_id` `workspace_id` |
| ไม่มี correlation | เพิ่ม `correlation_id` (RFC-0003 เขียนไว้เองใน Future Work) |
| ไม่มี cost | เพิ่ม cost attribution (Future Work ของ RFC-0003 เช่นกัน) |
| risk/authority | บันทึกทั้ง `action_risk` และ `authority` ที่ใช้ตัดสิน ไม่ใช่แค่ผลลัพธ์ ([ADR-0010](../../decisions/0010-risk-approval-taxonomy.md)) |
| observability depth | ต้องรองรับ trace ที่ไม่มี step ย่อย เพราะ external agent provider มองไม่เห็นข้างใน ([ADR-0005](../../decisions/0005-agent-runtime-boundary.md)) |

## ข้อกำหนดที่ตัดสินแล้วและจะไม่เปลี่ยน

**ห้ามเก็บ chain-of-thought ที่เป็น private reasoning** — เก็บเป็น structured audit metadata แทน (จาก `ref/enterprise-agent-backend-os-blueprint.md` §14)

ระหว่างที่ contract นี้ยังไม่มี ให้ producer เก็บ event ในรูปของตัวเองไปก่อนโดย**อย่าเผยแพร่เป็นสัญญาข้ามระบบ** — จะได้ไม่ต้องรื้อสองรอบ
