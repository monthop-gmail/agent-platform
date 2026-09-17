# policy/v1

## v1.4.0 — 2026-09-17

`Request.action.resource` มีมาตั้งแต่ `v1.0.0` เป็น `type: string` พร้อมตัวอย่างหนึ่งบรรทัด **และไม่มีกฎเลยสักข้อ** — ตัวอย่างในคำอธิบายมี namespace อยู่ในตัว แต่ไม่มีอะไรบังคับว่าต้องมี · `agent-platform` รายงานเองต่อโต๊ะว่าแกน *"ลงมือกับอะไร"* ที่หลายทีมกำลังออกแบบกันอยู่ **มีช่องอยู่แล้วในสัญญาของเรา และที่ไม่มีใครเห็นเป็นหนี้ของฝั่งเรา**

[ADR-0033](../../../decisions/0033-resource-must-carry-its-own-scope.md) เคาะ option C — **ปัญหาไม่ใช่ว่าไม่มีรูปแบบ แต่คือขอบเขตของค่าแคบกว่าขอบเขตที่กฎบังคับใช้**

ของจริงสี่ชนิดจากสองแหล่งที่ไม่ได้คุยกัน — MeshCentral `node_id` (unique ต่อ instance) · Zabbix host (ต่อ server + site) · discussion (ต่อ workspace) · workspace `ws-001` (**ชนข้าม deployment ตั้งแต่ค่าแรก**) · **ทั้งสี่ unique แคบกว่า tenant ซึ่งเป็นระดับที่นโยบายบังคับใช้**

### ความล้มเหลวมีสองทิศ และเป็นแผลคนละใบที่ปิดไปแล้วทั้งคู่

```text
deny เครื่องอันตรายที่ไซต์ A แล้วเชื่อว่าคุ้มทั้ง tenant  → ไม่คุ้มไซต์ B  = ADR-0026
เครื่องคนละเครื่องที่ไซต์ B บังเอิญได้ค่าเดียวกัน        → ถูกคุมทั้งที่ไม่ได้เขียนถึง = ADR-0027 ข้อ 5
```

อาการของทั้งสองทิศคือ **payload valid และ CI เขียว** — `type: string` รับได้หมด

### เพิ่มคำกำกับที่ฟิลด์ + `platform_rules` หกข้อ

`resource` ต้อง unique ภายใน tenant · ค่าที่แคบกว่านั้นต้องเติม `<namespace>:<local_id>` (ทาง MCP คือ `mcp/v1` `server_id` เหมือน `ToolId`) · **ชนแล้ว reject ไม่ใช่เลือกอันใดอันหนึ่ง** · การเติม namespace ต้องย้อนกลับได้ · `resource` ไม่ใช่ `CapabilityScope` และไม่ใช่ `action.type` — สามแกนตั้งฉากกัน ห้ามยุบ · กฎที่ไม่ระบุ `resource` ห้ามให้สิทธิ์แก่ action ที่มี `resource`

### ไม่ breaking — และตั้งใจไม่ใส่ `pattern`

เพิ่มคำอธิบายกับ `platform_rules` · **ไม่แตะ `type` ไม่ใส่ `pattern` ไม่ขยับ `required`** — รูปเดียวกับที่ [ADR-0027](../../../decisions/0027-toolid-transformation-must-be-deterministic.md) ตีพิมพ์กฎการแปลงใน `tool/v1` `v1.1.0` โดยไม่แตะ pattern ของ `ToolId`

ถ้าใส่ `pattern` payload ที่ส่งค่าเปล่าจะตกทันที ซึ่ง breaking ตาม [ADR-0006](../../../decisions/0006-contract-versioning.md) และบังคับให้ผู้ผลิตที่ยังไม่มี namespace หยุดรอ — ราคาที่ไม่จำเป็นในเมื่อกฎยังบังคับที่ผู้ผลิตอยู่ดี

⚠️ **กฎชุดนี้ validator กลางบังคับไม่ได้** ตรวจได้แค่ว่าค่าเป็น string — เขียนข้อจำกัดไว้ในตัวสัญญาแล้ว ไม่ปล่อยให้ผู้อ่านเชื่อว่าเครื่องบังคับให้ (หลักเดียวกับ [ADR-0030](../../../decisions/0030-the-field-nobody-named.md))

consumer ที่ pin ไว้ (`care-agent-platform` · `devfactory-core`) ไม่ต้องแก้อะไร — ค้นโค้ดแล้วยังไม่มีใครประกอบฟิลด์นี้ **แต่ควรไล่ดูว่าถ้าจะเริ่มส่ง ค่าที่ตัวเองมี unique ที่ขอบเขตไหน**

## v1.3.0 — 2026-08-21

`event/v1.policy_result` เคยประกาศรูปของตัวเอง ไม่ได้ `$ref` ไป `policy/v1` — มีสองที่ที่บอกว่า *"ผลของ policy หน้าตาอย่างไร"* และไม่มีอะไรคอยจับว่ายังตรงกัน · `consent` ที่ [ADR-0016](../../../decisions/0016-recording-which-consent-allowed-access.md) เพิ่มเข้า `Decision` ไม่ไหลไปที่นั่นเอง — พิสูจน์แล้วว่าเพี้ยนจริง ไม่ใช่ความเสี่ยงทางทฤษฎี

[ADR-0018](../../../decisions/0018-policy-result-single-source.md) เคาะ option B — **ปัญหาคือประกาศซ้ำ ไม่ใช่ย่อ**

* `$defs.DecisionSummary` — `effect` · `authority` · `action_risk` · `policy_id` · **ไม่มี `required`**
* `Decision` อ้าง Summary ผ่าน `allOf` แล้วประกาศเฉพาะส่วนที่เกิน (`constraint` `reason` `evaluated_at` `expires_at` `consent`)

### ชุดย่อยเป็นชุดย่อยโดยเจตนา

🔒 **field ใหม่ใน `Decision` ไม่ไหลเข้า Summary เอง — ต้องเคาะทุกครั้ง**

`reason` เป็น free text และ `expires_at` ไม่มีความหมายในบันทึกที่ immutable แล้ว · โดยเฉพาะ `reason` ที่ถ้าไหลเข้า audit เองจะเฉียดกับ guarantee ข้อ 7 ของ `event/v1` (*ห้ามเก็บ private reasoning เป็น audit record*) **โดยไม่มีใครตัดสินใจ** — ซึ่งเป็นเหตุผลที่ไม่เลือกทางยกทั้ง `Decision` ไปให้ event

### ไม่ breaking

ชุด property และ `required` ของ `Decision` **เท่าเดิมทุกตัว** — ย้ายที่ประกาศ ไม่ได้ย้ายความหมาย · payload ที่ valid กับ `v1.2.0` ยัง valid ทุกใบ

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
