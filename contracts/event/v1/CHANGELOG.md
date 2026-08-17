# event/v1

## v1.0.0 — 2026-08-18
- เขียนได้หลัง [`devfactory-core` RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) แยก authority เป็น semantics / wire schema
- semantics มาจาก `devfactory-core` `contract-semantics.yaml` `semantics_version: "1.0"` (RFC-0003 + RFC-0008)
- `job_id` optional · `subject_type` + `subject_id` required ตาม RFC-0008
- เพิ่ม field ระดับ platform: `tenant_id` `workspace_id` `correlation_id` `policy_result` `usage` `source` ตาม RFC-0005 Rule 1
- ตัดสินฝั่ง schema: **เก็บทั้ง `job_id` และ `subject_id`** เพราะเป็นคนละคำถาม (สายเหตุ vs หัวเรื่อง) พร้อมกฎว่าถ้า `subject_type: job` ต้องตรงกัน
