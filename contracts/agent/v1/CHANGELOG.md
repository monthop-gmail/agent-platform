# agent/v1

## v1.1.0 — 2026-09-02

เพิ่มบล็อก `policy` ที่ **ตัดออกได้อย่างเดียว** ตาม [ADR-0022](../../../decisions/0022-agent-may-narrow-its-own-scope.md) จาก [issue #47](https://github.com/monthop-gmail/agent-platform/issues/47)

`profile/v1` เขียนกฎไว้เองว่า *"สิทธิ์จริงคือส่วนที่ profile, agent และ policy ของ tenant ตกลงตรงกัน**ทั้งสามฝ่าย**"* แต่ฝ่าย agent มีแค่ `tools` (ขอ) · `capability_requirement` (ต้องการ) · `policy_profile` (ชื่อเพดาน) — **ทั้งสามคือการขอ ไม่มีที่ให้สละสิทธิ์** · "สามฝ่าย" จึงเป็นสองฝ่ายบวกผู้ยื่นคำขอมาตลอด

* `policy.deny_tools` · `policy.deny_capabilities` · `policy.require_human_for`
* `additionalProperties: false` — **ไม่มี `allow` ทุกชนิด และไม่มี `authority_map`**

### ทำไม "ไม่ได้ขอ" ไม่เท่ากับ "ห้าม"

`mcp_servers` เป็นรายการ id ของ server — **tool ที่มาจากที่นั่นไม่ได้ถูกแจกแจงใน `tools`** agent จึงได้ tool ที่ไม่เคยระบุมาโดยไม่มีทางปฏิเสธ · และการไม่ใส่แยกไม่ออกจากการลืมใส่

### ปลอดภัยโดยโครงสร้าง ไม่ใช่โดยวินัย

ถ้ามี `allow` ฝั่ง agent กฎ *"ค่าที่กว้างที่สุดชนะไม่ได้"* จะถูกละเมิดทันที · **การที่บล็อกนี้ตัดออกได้อย่างเดียวโดยนิยาม คือสิ่งที่ทำให้มันปลอดภัยพอจะมี** — `additionalProperties: false` ทำให้เติม `allow` เข้ามาทีหลังแบบเงียบ ๆ ไม่ได้

### กฎการรวมที่ implementation ต้องบังคับ

`allow` → intersection · `deny` → union (ของฝ่ายใดก็ชนะ) · และ `required` ของ agent+profile **ต้องไม่ตัดกับ deny ของฝ่ายใดเลย** ถ้าตัดกัน = การผูก agent เข้ากับ profile นั้น **invalid ให้ reject ไม่ใช่ลดให้เงียบ ๆ**

### ไม่ breaking

optional · `required` ยัง 5 ตัวเท่าเดิม · **ยังไม่มี consumer รายไหน pin `agent/v1`**

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม `ref/agent-platform-contract-review.md` (P0) และ [ADR-0009](../../../decisions/0009-capability-model.md)
- agent ระบุ **capability requirement** ไม่ใช่ provider — routing เป็นคนเลือก
