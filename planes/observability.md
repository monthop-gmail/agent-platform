# Observability — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | ยังไม่มี repo · `devfactory-core/packages/observability` เป็นของฝั่ง job |
| Contracts | [`event/v1`](../contracts/event/v1/) 🔗 derived · `execution/v1` · `error/v1` |
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

## สถานะ

[`contracts/event/v1`](../contracts/event/v1/) เขียนแล้ว (2026-08-18) — `job_id` optional · `subject_type`/`subject_id` required · `correlation_id` · `tenant_id` required · `policy_result` บันทึกทั้ง `action_risk` และ `authority`

semantics (event vocabulary 7 ตัว + guarantees) เป็นของ `devfactory-core` แก้ที่นี่ไม่ได้ ต้องมี RFC ที่ต้นทางก่อน ([ADR-0006 C2](../decisions/0006-contract-versioning.md))

ยังไม่มี implementation — dashboard, metrics backend และ replay engine ยังไม่มี repo
