# model/v1

## v1.1.0 — 2026-09-02

แก้ถ้อยคำของ `Request.model_id` + เพิ่ม `platform_rules` ตาม [ADR-0023](../../../decisions/0023-frozen-bindings-and-identity.md) จาก [issue #46](https://github.com/monthop-gmail/agent-platform/issues/46)

ถ้อยคำเดิม (*"ระบุตอน runtime เท่านั้น"*) เขียนถึง **task schema** แต่ถูกอ่านเป็น **ทุกที่ที่ชื่อ model ปรากฏได้** — `agent-builder-dsh-poc` จึงต้องมาถามว่า `CompiledAgent` ที่มี binding ฝังอยู่ผิดหรือเปล่า และ consumer รายถัดไปที่อ่านจะสรุปว่าเขาผิด

```text
package.json      ประกาศช่วง            ←  capability_requirement
package-lock.json บันทึกผลที่ resolve   ←  build artifact
```

**lockfile ไม่ใช่การ hard-code** — การห้ามบันทึกผลการ resolve จะทำให้ build ที่ทำซ้ำได้เป็นไปไม่ได้ และผลักให้คน hard-code จริง ๆ แทน ซึ่งเป็นสิ่งที่ข้อห้ามนี้ตั้งใจกัน

### แต่รับพร้อมเงื่อนไข ไม่ใช่รับเปล่า

ผู้ขอเจอบั๊กของตัวเองระหว่างเขียน issue — `manifestChecksum` คำนวณจาก manifest อย่างเดียว **catalog เปลี่ยนแล้ว checksum เท่าเดิมแต่รันด้วย model คนละตัว** · การตอบว่าถูกต้องโดยไม่พูดเรื่องนี้คือการรับรองบั๊กนั้นไปด้วย

`platform_rules` จึงระบุเงื่อนไขสามข้อ และข้อ 3 (**identity ของสิ่งที่ build ต้องครอบ binding**) คือข้อที่ทำให้อีกสองข้อตรวจสอบได้

### ใครเป็นเจ้าของผลการ resolve

**ไม่มีใคร เพราะไม่ใช่การตัดสิน** — เป็นหลักฐานว่า ณ เวลานั้น catalog ตอบว่าอะไร · ต้อง**แช่แข็งผล**ไม่ใช่เก็บตัวชี้ ตามเกณฑ์ของ [ADR-0019](../../../decisions/0019-execution-records-its-approval.md): *สิ่งที่ชี้ไปเปลี่ยนได้ไหม* — catalog เปลี่ยนได้

### ไม่ breaking

ไม่มี field เปลี่ยน · `Request.required` ยัง 4 ตัวเท่าเดิม · เป็นการเขียนความหมายที่ตั้งใจไว้แต่แรกให้ตรง

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0004](../../../decisions/0004-agent-vs-model-provider.md)
- `inference` — request / response / usage สำหรับ model provider เท่านั้น
