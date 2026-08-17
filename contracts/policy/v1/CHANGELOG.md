# policy/v1

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0010](../../../decisions/0010-risk-approval-taxonomy.md)
- แยก `effect` (allow/deny) ออกจาก `authority` (ใครอนุมัติ) และ `constraint` (rate/budget)
  แทนที่จะยัดเป็น enum เดียว 5 ค่าแบบ backend-os §8 — เพราะ rate-limit ไม่ใช่ "decision" ที่มี authority
- `approval` (คำตัดสินของผู้มีอำนาจ) อยู่คนละ contract และยัง `external-authority-pending`
