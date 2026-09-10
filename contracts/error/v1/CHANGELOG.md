# error/v1

## v1.1.0 — 2026-09-10
- `details` มีกฎแล้ว — เดิมเป็น `type: object` เปล่า ไม่มีคำอธิบายสักบรรทัด ขณะที่ `message`
  ที่อยู่ติดกันในไฟล์เดียวกันห้าม PII ไว้ตั้งแต่ v1.0.0 · ความไม่สมมาตรนี้ไม่มีใครเห็นมาสามสัปดาห์
- พบโดย [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) ระหว่างไล่ปิด
  `metadata` ของ `event/v1` ในบ้านตัวเอง แล้วเดินผ่าน `details` ไปโดยไม่เห็น จนย้อนกลับมาเจอเอง
  ([ADR-0030](../../../decisions/0030-the-field-nobody-named.md))
- **ไม่ breaking** — เพิ่มคำอธิบายและกฎ ไม่แตะ type ไม่แตะ `required` ไม่ปิด object

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม `ref/agent-platform-decisions-first-plan.md` Phase 3
- แยก `policy_denied` และ `approval_required` ออกจาก `authorization` เพราะ retry semantics ต่างกัน
