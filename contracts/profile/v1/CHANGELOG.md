# profile/v1

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม `ref/agent-platform-decisions-first-plan.md` Phase 4
- เป็น contract **เพิ่มเติมจากลิสต์ P0 เดิม** — เพิ่ม contract ใหม่ไม่ใช่ breaking change ([ADR-0006](../../../decisions/0006-contract-versioning.md))
  แต่บันทึกไว้ให้ชัดว่าเป็นการขยายขอบเขต ไม่ใช่ของที่อยู่ในลิสต์ตั้งแต่แรก
- `authority_map` บังคับให้ mapping `action_risk → authority` เป็น config ตาม [ADR-0010](../../../decisions/0010-risk-approval-taxonomy.md)
