# profile/v1

## v1.1.0 — 2026-09-02

เขียนกฎที่ยังไม่เคยเขียน + ต่อสายที่มีอยู่แล้ว ตาม [ADR-0026](../../../decisions/0026-tool-identity-ceiling-is-namespace-bound.md) จาก [issue #53](https://github.com/monthop-gmail/agent-platform/issues/53)

**ไม่มี field ใหม่ ไม่มี field เปลี่ยน type · `required` ไม่ขยับ**

### ปัญหาที่ #53 รายงาน และด้านที่อันตรายกว่าซึ่งเจอตอนตรวจ

profile ที่เขียนด้วยชื่อจาก namespace หนึ่ง เอาไปใช้กับ agent ที่มี tool อีก namespace:

| | ผลลัพธ์ | ทิศทาง |
| --- | --- | --- |
| `allow` ไม่ตรงเลย | ไม่มี tool เหลือ | ❌ fail **closed** — พังให้เห็น |
| `deny` ไม่ตรงเลย | **ไม่ปิดอะไรเลย** | ☠️ fail **open** — *"profile นี้ห้าม merge"* กลายเป็นความเชื่อที่ไม่จริง **เงียบ ๆ** |

> profile ที่เขียนด้วยชื่อจาก namespace หนึ่ง ไม่ได้แปลว่าไม่มีผลกับอีก namespace — **มันแปลว่าไม่มีใครรู้ว่ามันมีผลหรือเปล่า**

### กฎ 4 ข้อที่เขียนลงสัญญา

```text
1. ไม่มี tools.allow = ไม่มีเพดานเชิงชื่อ · allow: [] = ไม่อนุญาตเลย
   — เดิม schema เขียนแค่ "ว่าง = ไม่อนุญาต" ไม่เคยบอกว่าไม่มี field เลยแปลว่าอะไร
2. tool ที่ required_capabilities ตัดกับ deny_capabilities ของฝ่ายใด → ใช้ไม่ได้
3. allow ที่ไม่ตรงเลยสักตัว = ใช้ผิด namespace → reject ไม่ใช่ deny-all เงียบ ๆ
4. deny และ require_human_for เชิงชื่อ ปกป้องเฉพาะ namespace ที่มันตั้งชื่อ
```

**ข้อ 2 คือการต่อสายที่ควรมีตั้งแต่แรก** — `tool/v1` ประกาศ `required_capabilities` ไว้ตั้งแต่ v1.0.0 แต่ `grep -rn required_capabilities contracts/` ได้ผลลัพธ์เดียวคือที่นิยามตัวเอง · ต่อแล้วเพดานเชิงคุณสมบัติ **ทำงานกับ tool registry ที่ platform ไม่เคยเห็น** ซึ่งเป็นอย่างเดียวที่ platform เขียนได้จริง

**ข้อ 3 ตอบด้าน fail-closed · ข้อ 4 ตอบด้าน fail-open** — ข้อ 4 ไม่ได้ทำให้ deny เชิงชื่อทำงานข้าม namespace (ทำไม่ได้) แต่ทำให้ไม่มีใครเข้าใจผิดว่ามันทำ

### profile ทั้ง 6 ตัวไม่ต้องแก้

ยังเป็นเพดานที่ถูกต้องสำหรับ tenant ที่ใช้ namespace กลาง · สิ่งที่เปลี่ยนคือการเอาไปใช้กับ namespace อื่นจะถูก **reject** แทนที่จะกลายเป็น deny-all เงียบ ๆ · ตรวจแล้วทั้ง 6 ยัง validate ผ่าน

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม `ref/agent-platform-decisions-first-plan.md` Phase 4
- เป็น contract **เพิ่มเติมจากลิสต์ P0 เดิม** — เพิ่ม contract ใหม่ไม่ใช่ breaking change ([ADR-0006](../../../decisions/0006-contract-versioning.md))
  แต่บันทึกไว้ให้ชัดว่าเป็นการขยายขอบเขต ไม่ใช่ของที่อยู่ในลิสต์ตั้งแต่แรก
- `authority_map` บังคับให้ mapping `action_risk → authority` เป็น config ตาม [ADR-0010](../../../decisions/0010-risk-approval-taxonomy.md)
