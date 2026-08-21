# policy/v1

## v1.2.0 — 2026-08-21

`Request` เรียกผู้กระทำว่า `subject` ขณะที่ `consent/v1` เขียนกำกับ field ชื่อเดียวกันไว้เองว่า 🔒 *"ไม่ใช่ actor"* — [ADR-0017](../../../decisions/0017-the-word-subject.md) ไล่ทั้ง `contracts/` แล้วพบว่าคำนี้ถูกใช้ใน **5 contract 3 ความหมาย** และวินิจฉัยว่า **`subject` = สิ่งที่บันทึกนั้นเกี่ยวกับ · ผู้กระทำคือ `actor`** ซึ่งทำให้ 4 ใน 5 ถูกอยู่แล้ว และเหลือไฟล์นี้ไฟล์เดียวที่ต้องแก้

* `$defs.Actor` — นิยามรูปครั้งเดียว
* `Request.actor` — ชื่อใหม่ · `Request.subject` ติด `deprecated: true` รูปเหมือนเดิมทุกอย่าง
* `Request.required` ถอด `subject` ออก เหลือ `[context, action]` แล้วใช้ **`oneOf` บังคับให้มีอย่างใดอย่างหนึ่ง ห้ามมีทั้งคู่**

### ไม่ breaking

payload เดิมที่ส่ง `subject` **ยัง valid ทุกใบ** · การถอดออกจาก `required` เป็นการผ่อน ไม่ใช่บังคับ · `oneOf` ห้ามส่งสองชื่อพร้อมกัน แต่ `actor` เพิ่งเกิด **จึงไม่มี payload เดิมใบไหนส่งทั้งคู่ได้** ไม่มีใบไหนกลายเป็น invalid

`care-agent-platform` และ `devfactory-core` ที่ pin อยู่ **ไม่ต้องทำอะไรทันที** — ย้ายไป `actor` เมื่อสะดวก

### ⏳ ต้องลบใน `policy/v2`

`subject` มีอยู่เพื่อไม่ให้ใครต้องขึ้น major เพราะชื่อเท่านั้น · **v2 ที่เกิดด้วยเหตุอื่นต้องลบมันทิ้งพร้อมกัน** ไม่ใช่ปล่อยไว้เป็นชื่อที่สองถาวร

### ที่ไม่แตะ

`event/v1` และ `approval/v1` ใช้ `subject` ในความหมายที่ถูกตามคำวินิจฉัยอยู่แล้ว และเป็น 🔒 semantics ของ `devfactory-core` ที่เปลี่ยนที่นี่ไม่ได้ · `consent/v1.subject_id` เป็น **data subject** ตามศัพท์กฎหมาย ซึ่ง ADR-0017 อนุญาตไว้เป็นข้อยกเว้น · ทั้งสามได้หมายเหตุอ้างอิงไขว้แทนการเปลี่ยนชื่อ

## v1.1.0 — 2026-08-21

เพิ่ม **ผลการประเมินความยินยอม** ตาม [ADR-0016](../../../decisions/0016-recording-which-consent-allowed-access.md) (option C)

`consent_rules` ข้อ 6 บังคับว่าการเข้าถึงต้องผ่านทั้ง `policy/v1` และ consent แต่ไม่มี record ไหนบอกได้ว่า **อนุญาตด้วยความยินยอมใบไหน** — และหลัง [ADR-0014](../../../decisions/0014-consent-access-time-conditions.md) การเก็บแค่ `grant_id` ก็ยังไม่พอ เพราะใบที่มี `conditions` ตอบตัวเองไม่ได้ ประเมินใหม่ทีหลังจะได้คำตอบของ *วันที่ประเมิน* ไม่ใช่ของ *วันที่เข้าถึง*

* `Request.consent` — optional input · `$ref` ไป `consent/v1#/$defs/Evaluation`
* `Decision.consent` — สำเนาของสิ่งที่ได้รับมา หลักเดียวกับ `action_risk` ที่บันทึกสิ่งที่ใช้ตัดสิน ไม่ใช่แค่ผลลัพธ์

### 🔒 policy ไม่ได้เป็นคนประเมิน consent

`Request` เดิมมีแค่ `context` · `subject` (ผู้กระทำ) · `action` — **ไม่มี field ไหนบอกว่าเป็นข้อมูลของใคร** สองด่านถูก AND กันโดยผู้เรียก ไม่ใช่โดย policy engine

field นี้จึงเป็น **input ที่ผู้เรียกประเมินมาแล้วส่งเข้ามา** ให้ policy *ใช้ประกอบ* การตัดสินได้ (เช่นกฎ "ไม่มีใบที่ยังใช้ได้ = deny") ไม่ใช่ให้ policy ไปตรวจเอง

* **ไม่มี `Request.consent` = ผู้เรียกไม่ได้ส่งมา ไม่ได้แปลว่าไม่ต้องมีความยินยอม**
* **ห้ามเติม `Decision.consent` เองถ้าไม่ได้รับมา** — record ที่อ้างว่าพิจารณาสิ่งที่ไม่เคยเห็นคือ audit ที่โกหก

### ไม่ breaking

optional ทั้งคู่ · `required` ของ `Request` (3) และ `Decision` (4) ไม่ขยับ

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0010](../../../decisions/0010-risk-approval-taxonomy.md)
- แยก `effect` (allow/deny) ออกจาก `authority` (ใครอนุมัติ) และ `constraint` (rate/budget)
  แทนที่จะยัดเป็น enum เดียว 5 ค่าแบบ backend-os §8 — เพราะ rate-limit ไม่ใช่ "decision" ที่มี authority
- `approval` (คำตัดสินของผู้มีอำนาจ) อยู่คนละ contract — ดู [`approval/v1`](../../approval/v1/)
