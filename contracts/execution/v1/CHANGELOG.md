# execution/v1

## v1.2.0 — 2026-09-02

เพิ่ม `provider_switches` ตาม [ADR-0025](../../../decisions/0025-provider-switch-and-what-identity-covers.md) จาก [issue #52](https://github.com/monthop-gmail/agent-platform/issues/52)

`provider_id` เป็น string ตัวเดียว — execution ที่ย้าย provider กลางรอบเมื่อโดน 429/5xx จึงบันทึกได้แค่ตัวเดียว **ทั้งที่ครึ่งหลังรันด้วยอีกตัว** · record ที่อ่านแล้วได้ความจริงไม่ครบ แบบเดียวกับที่ [ADR-0013](../../../decisions/0013-approval-supersedes-chain.md) · [ADR-0016](../../../decisions/0016-recording-which-consent-allowed-access.md) · [ADR-0019](../../../decisions/0019-execution-records-its-approval.md) ปิดไปแล้วสามครั้ง

**ไม่ใช่กรณีสมมติ** — `agent-builder-dsh-poc` ชน 429/502/503 ห้าครั้งใน 8 attempt กับ endpoint ฟรีจริง

* `provider_switches` — array, `minItems: 1` · `{from, to, at, reason}` · `additionalProperties: false`
* `reason` ใช้ `error/v1` `$defs.Category` ที่มีอยู่แล้ว **ไม่ตั้ง enum ใหม่**
* `provider_id` เขียนกำกับว่าหมายถึง **ตัวที่มีผลล่าสุด ไม่ใช่ตัวเดียวที่เคยใช้**

### 🔒 platform ไม่ได้ตัดสินว่าใครเป็นคนย้าย

router หรือ adapter ก็ได้ — **สิ่งที่บังคับคือถ้าย้ายแล้วต้องบันทึก** · สัญญานี้เป็นเจ้าของ *บันทึก* ไม่ใช่ *วิธีทำ*

### ⚠️ `usage` ของ execution ที่ย้าย provider ใช้คิด cost ตรง ๆ ไม่ได้

รวม token จากหลาย provider ที่ราคาต่อ token คนละอัตราเข้าด้วยกัน · **เขียนเป็นกฎไว้ก่อน ยังไม่สร้าง field** เพราะยังไม่มี consumer รายไหนคำนวณ cost จริง — การออกแบบรูปตอนนี้คือเดารูปให้งานที่ยังไม่มีใครทำ

### ไม่ breaking

optional · `required` ยัง 5 ตัวเท่าเดิม · `provider_id` ไม่เปลี่ยน type และความหมายไม่เปลี่ยนสำหรับ execution ที่ไม่เคยย้าย

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
