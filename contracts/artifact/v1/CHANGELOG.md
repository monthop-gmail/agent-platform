# artifact/v1

## v1.1.0 — 2026-10-17

`checksum` ประกาศความหมายของความว่าง + ช่อง `covers` (optional) ([ADR-0036](../../../decisions/0036-a-checksum-that-cannot-be-verified.md))

ช่องนี้ตั้งต้นเมื่อ 17 ส.ค. แล้วไม่เคยแก้ · โผล่มาตอนทำ `approval/v1` `payload_digest` เพราะ [ADR-0035](../../../decisions/0035-approval-bound-to-an-id-is-not-bound-to-what-runs.md) Option C **ยืมรูป `{algorithm, value}` มาจากไฟล์นี้** แล้วพอเปิดมาลอกรูป ก็พบว่าตัวแบบเองไม่มีกฎ

### สามสภาพที่ต่างกันจริง ยุบเป็นสภาพเดียว

```text
ไม่มี checksum เลย         valid    ← สภาพเดียวที่ซื่อสัตย์
checksum: {}               valid    ประกาศว่ามี checksum โดยไม่มี
checksum: {value: "abc"}   valid    แฮชที่ตรวจไม่ได้ เพราะไม่รู้อัลกอริทึม
```

และ `checksum` **ไม่อยู่ใน `required` พร้อมกับ `uri`** จึงมีใบที่พกแฮชของสิ่งที่ตัวใบไม่ได้บอกว่าอยู่ไหน · `uri` ชี้ไป storage ที่เนื้อเปลี่ยนได้โดยที่ `artifact_id` ไม่เปลี่ยน — `checksum` คือช่องเดียวที่จับข้อนั้นได้

[ADR-0023](../../../decisions/0023-frozen-bindings-and-identity.md) เขียนไว้ตั้งแต่ 20 ก.ย. ว่า **"checksum ที่อ้างมากกว่าสิ่งที่มันครอบ คือ false"** — แล้วไฟล์นี้ละเมิดมันอยู่

### ทำไมรอบนี้ยังไม่บังคับ

`required: [algorithm, value]` · `additionalProperties: false` · `pattern` ที่ `value` — **เข้านิยาม breaking ของ [ADR-0006](../../../decisions/0006-contract-versioning.md) ทั้งสามข้อ** (*"เข้มขึ้นใน validation"* · *"optional → required"*) จึงเป็นงานของ `artifact/v2`

และเหตุที่เรื่อง breaking เป็นเรื่องจริงไม่ใช่เรื่องทฤษฎี — ทะเบียนบันทึกว่า **ไม่มีใคร pin `artifact/v1`** แต่

```text
contracts/execution/v1/execution.schema.yaml:146   artifacts: items: $ref → artifact/v1
execution/v1 ถูก pin โดย  devfactory-core ✅ passing  ·  agent-builder-dsh-poc ✅ passing
```

**ผู้ผลิตที่ส่ง `execution/v1` พร้อม `artifacts[]` ใช้ `artifact/v1` อยู่โดยไม่เคย pin มัน** · ทะเบียนนับการประกาศ ไม่ได้นับการเอื้อมถึงผ่าน `$ref`

### ไม่ breaking — และตรวจทางที่ผู้ผลิตใช้จริงด้วย

```text
15 เคส FAIL=0 · เจ็ดเคสแรกคือทุกรูปที่ valid ก่อน v1.1.0
  {} · {value} · {value:''} · algorithm อย่างเดียว · ช่องเกินในบล็อก    valid ทั้งหมด ✅
  covers: [] · [''] · ไม่ใช่ array                                   invalid ✅
execution/v1 + artifacts[0].checksum = {value:"abc"}                valid ✅ ไม่ breaking
```

### ที่ยังไม่ได้ และไม่ใช่การลืม

`v1.1.0` ซื้อ **ผู้อ่านรู้ตัว** ไม่ได้ซื้อ **validator ปฏิเสธ** — สองอย่างนี้ไม่ใช่สิ่งเดียวกัน และ ADR-0036 เขียนข้อนี้ไว้เป็นข้อเสียของทางที่เลือก · ระหว่างนี้รีโปจะมีสองมาตรฐานของ checksum (`approval/v1.payload_digest` เข้ม · `artifact/v1.checksum` หลวม) ซึ่งยอมรับอย่างรู้ตัว

ขั้นถัดไปคือถาม `devfactory-core` และ `agent-builder-dsh-poc` ว่าส่ง `artifacts[].checksum` อยู่ไหมและรูปไหน — **คำตอบนั้นคือสิ่งที่ทำให้ตัดสิน `v2` ด้วยหลักฐานแทนการเดา**

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม `ref/agent-platform-contract-review.md` (P2) และ module mapping
