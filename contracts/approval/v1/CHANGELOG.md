# approval/v1

## v1.0.0 — 2026-08-18
- เขียนได้หลัง [`devfactory-core` RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) แยก authority เป็น semantics / wire schema — ไม่ติด `external-authority-pending` อีกต่อไป
- semantics มาจาก `devfactory-core` `contract-semantics.yaml` `semantics_version: "1.0"`
- field ระดับ platform (`tenant_id` `workspace_id` `execution_id` `agent_id` `policy_id` `expires_at` `action_risk` `escalation_target`) เพิ่มได้ผ่าน ADR ฝั่งนี้อย่างเดียวตาม RFC-0005 Rule 1
