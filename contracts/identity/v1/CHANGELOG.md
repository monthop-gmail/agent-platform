# identity/v1

## v1.1.0 — 2026-08-22

* `WorkspaceId` เขียนให้ชัดว่าเป็น **ขอบเขตอนุญาต ไม่ใช่กำแพง** — [ADR-0021](../../../decisions/0021-workspace-is-a-scope-not-a-boundary.md)

`enterprise-knowledge` เปิด [#23](https://github.com/monthop-gmail/enterprise-knowledge/issues/23) ถามว่า `workspace_id` เข้มเท่า `tenant_id` ไหม ก่อนจะเขียน `schema.sql` — [ADR-0007](../../../decisions/0007-multi-tenancy.md) พูดสองอย่างที่ต้องอ่านคู่กัน (*"workspace = grouping"* กับเหตุผลที่ปฏิเสธ option C ว่า *"ไม่มี workspace แล้วทีมหนึ่งเห็น knowledge อีกทีมทั้งหมด"*) แล้วไม่เคยมีใครเคาะว่าตกลงบังคับแค่ไหน

| | `tenant_id` | `workspace_id` |
| --- | --- | --- |
| ข้ามได้ไหม | ไม่ได้ทุกกรณี | **deny by default แต่อนุญาตได้** ผ่าน `policy/v1` |
| บังคับที่ชั้นไหน | ชั้นเก็บข้อมูล (RLS/partition) | ชั้นตรวจสิทธิ์ |
| การข้ามที่สำเร็จ | ไม่มี | **ต้องออก audit event เสมอ** |

**ไม่มี field เปลี่ยน ไม่มีอะไร breaking** — เป็นการเขียนความหมายที่ ADR-0007 ตัดสินไว้แล้วให้ชัดขึ้น ตรงที่คนอ่านจริง

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0007](../../../decisions/0007-multi-tenancy.md)
- `TenantId` `WorkspaceId` `ActorId` `AgentId` `ExecutionId` `Principal` `RequestContext` `ExecutionContext`
