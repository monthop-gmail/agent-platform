# Observability — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | ยังไม่มี repo · `devfactory-core/packages/observability` เป็นของฝั่ง job |
| Contracts | `contracts/event/` ⏳ **pending** · `execution/v1` · `error/v1` |
| ADR | [0006](../decisions/0006-contract-versioning.md) · [0007](../decisions/0007-multi-tenancy.md) · [0010](../decisions/0010-risk-approval-taxonomy.md) |

## รับผิดชอบ

```text
Agent → Reason/Plan metadata → Tool Call → Policy Decision → Execution → Result
```

* trace ของทุก execution, tool call, policy decision
* cost attribution ต่อ tenant / workspace / agent
* audit trail ที่ **append-only** และไม่มี silent state change
* replay ของ execution เพื่อ debug และเพื่อป้อนเข้า [`evals`](evals.md)

## กฎที่ตัดสินแล้วและจะไม่เปลี่ยน

* **ห้ามเก็บ chain-of-thought ที่เป็น private reasoning** — เก็บเป็น structured audit metadata แทน
* บันทึกทั้ง `action_risk` และ `authority` ที่ใช้ตัดสิน ไม่ใช่แค่ผลลัพธ์ ([ADR-0010](../decisions/0010-risk-approval-taxonomy.md)) เพราะ audit ย้อนหลังต้องรู้ว่าตัดสินจากอะไร
* ต้องรองรับ trace ที่ **ไม่มี step ย่อย** เพราะ external agent provider มองไม่เห็นข้างในตัวเอง — ห้ามตีความว่าเป็น execution ที่ไม่ได้ทำอะไร
* ทุก event ต้องมี `tenant_id` ([ADR-0007](../decisions/0007-multi-tenancy.md))

## ห้ามทำ

* บล็อก execution เพราะ observability พัง — trace หายดีกว่างานหยุด แต่ต้องนับว่าหายไปเท่าไร
* เก็บ credential, PII หรือเนื้อหา prompt ผู้ใช้ในข้อความ error ([`error/v1`](../contracts/error/v1/))

## สถานะ ⏳

**`contracts/event/` ยังไม่เขียน** — มาจาก `devfactory-core` RFC-0003 ที่ authority ยังไม่ย้าย ([issue #6](https://github.com/monthop-gmail/agent-platform/issues/6))

สิ่งที่ต้องแก้จาก RFC-0003 ก่อนใช้ระดับ platform อยู่ใน [`contracts/event/README.md`](../contracts/event/README.md) — `job_id` required → optional, field 5 → 13 ตัว, correlation id, cost attribution

ระหว่างนี้ producer เก็บ event รูปแบบตัวเองได้ แต่ **อย่าเผยแพร่เป็นสัญญาข้ามระบบ**
