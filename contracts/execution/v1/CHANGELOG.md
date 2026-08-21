# execution/v1

## v1.1.0 — 2026-08-21

`approval/v1` `guarantees` ข้อ 3 (🔒 frozen) เขียนว่า *"execution ที่ไม่มี APPROVE เป็นสิ่งที่ห้าม"* แต่ `execution/v1` มี `policy_decision` เต็มใบ (จึงรู้ว่า **ต้องขออนุมัติไหม**) และไม่มี field ไหนชี้ไปยังใบอนุมัติได้เลย — [ADR-0019](../../../decisions/0019-execution-records-its-approval.md) option A

* `approval_id` (optional) — ใบอนุมัติที่อนุญาตให้ execution นี้เดินต่อ

### ทำไมเก็บ id ก็พอ ทั้งที่ ADR-0016 บอกว่าไม่พอ

`approval/v1` `guarantees` ข้อ 1 บอกว่า decision เป็น **immutable** — ใบที่อ่านปีหน้าให้คำตอบเดียวกับที่อ่านวันนี้เสมอ · ต่างจาก `consent/v1` ที่ใบมี `conditions` ซึ่งเปลี่ยนคำตอบได้ จึงต้องแช่แข็ง **ผลการประเมิน** ไว้

> เกณฑ์คือ **สิ่งที่ชี้ไปเปลี่ยนได้ไหม** ไม่ใช่กฎเหมารวมว่าห้ามเก็บ id

### ⚠️ ไม่มีค่านี้ไม่ได้แปลว่าผิดเสมอ

execution ที่จบที่ `rejected` · `cancelled` · `timed_out` **ไม่มี APPROVE ให้ชี้ตามนิยาม** — ถูกปฏิเสธหรือยกเลิกก่อนมีใครอนุมัติ

จึงไม่ใส่ `if/then` บังคับตาม `authority` แม้จะเขียนได้ เพราะจะแดงกับเส้นทางที่ถูกต้อง — **สัญญาณลวงอันตรายพอ ๆ กับการตรวจไม่เจอ**

### invariant ที่ผู้ผลิตต้องบังคับเอง

ใบที่อ้างต้องมีอยู่จริง · `tenant_id` เดียวกัน · `subject` ตรงกับ execution นี้ · `decision` ต้องเป็น `APPROVE` (`REJECT`/`REQUIRE_CHANGES` อ้างไม่ได้) · ต้องมีก่อนออกจาก `awaiting_approval` ไปสู่ `running`

### ไม่ breaking

optional · `required` ยัง 5 ตัวเท่าเดิม · payload ที่ valid กับ `v1.0.0` ยัง valid ทุกใบ

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0005](../../../decisions/0005-agent-runtime-boundary.md) option C2
- state machine ระดับ execution เป็นของ platform เอง — RFC-0001 ครอบแค่ระดับ job
- ตอบ open question ของ RFC-0001: retry semantics และ parallel substates
- `job_id` เป็น optional · ความหมายของ job state เป็นของ `devfactory-core` (RFC-0001 + RFC-0007) ซึ่งให้ vocabulary 13 states มาแล้วใน `contract-semantics.yaml`
