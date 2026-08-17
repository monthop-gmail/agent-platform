# execution/v1

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0005](../../../decisions/0005-agent-runtime-boundary.md) option C2
- state machine ระดับ execution เป็นของ platform เอง — RFC-0001 ครอบแค่ระดับ job
- ตอบ open question ของ RFC-0001: retry semantics และ parallel substates
- `job_id` เป็น optional และความหมายของ job state ยัง `external-authority-pending` (ADR-0006)
