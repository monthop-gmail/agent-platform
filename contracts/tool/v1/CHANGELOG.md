# tool/v1

## v1.1.0 — 2026-09-03

เพิ่ม `platform_rules` — **กฎการแปลงชื่อเป็น `ToolId`** ตาม [ADR-0027](../../../decisions/0027-toolid-transformation-must-be-deterministic.md) จาก [issue #59](https://github.com/monthop-gmail/agent-platform/issues/59)

**ไม่แตะ `ToolId` pattern · ไม่มี field ใหม่ · `required` ไม่ขยับ**

### ข้อมูลที่เปลี่ยนคำถาม

`agent-builder-dsh-poc` probe MCP จริงด้วย `listTools()` — 29 tool จาก 2 server **เป็นชื่อเปล่าทั้งหมด และผ่านทั้งหมดเมื่อเติม namespace** · แต่ connector บุคคลที่สามหนักกว่า:

| server | รูปแบบ | เติม namespace แล้ว |
| --- | --- | --- |
| Canva | kebab-case (33 ตัว) | ❌ ยังไม่ผ่าน — ขีดกลาง |
| Composio | SCREAMING_SNAKE (7 ตัว) | ❌ ยังไม่ผ่าน — ตัวใหญ่ |

`ToolId` ไม่ได้บังคับแค่ *"ต้องมีจุด"* — **แต่ละ segment ต้องเป็น `[a-z][a-z0-9_]*`** ด้วย · **การเติม namespace อย่างเดียวไม่พอ ต้อง sanitize**

### คำถามจึงไม่ใช่ "ผ่อนไหม" แต่เป็น "ใครกำหนดการแปลง"

ถ้าแต่ละ consumer แปลงเอง **tool ตัวเดียวกันมี `ToolId` คนละชุด** → `deny` ที่ profile เขียนไว้คุ้มรายหนึ่งแต่ไม่คุ้มอีกราย **ทำลายฐานของ [ADR-0026](../../../decisions/0026-tool-identity-ceiling-is-namespace-bound.md) ที่เพิ่งวางไว้** — และเสียหายเพราะข้อบังคับของเราเอง

### กฎ 6 ข้อ

1. ชื่อภายใน ≠ ชื่อบน wire — map ที่ขอบเขตเดียว (แบบเดียวกับ `devfactory-core` `WIRE_FIELD_NAMES`)
2. lowercase → อักขระนอก `[a-z0-9_]` เป็น `_` ทีละตัว **ห้ามยุบซ้ำ** → เติม namespace
3. แปลงแล้วยังไม่ match → **reject บังคับ mapping มือ ห้ามเดา prefix**
4. แปลงแล้วชนกัน → **reject ไม่ใช่เลือกอันใดอันหนึ่ง**
5. **การแปลงต้องย้อนกลับได้** — เก็บชื่อเดิมไว้ให้ audit ตามกลับได้
6. `ToolId` unique ภายใน tenant ไม่ใช่ทั้งโลก

**ข้อ 4 สำคัญที่สุด** — การชนเกิดจากการแปลงของเราเอง ไม่ใช่ความผิดของ server · ปล่อยเงียบแปลว่า tool คนละตัวอยู่หลัง id เดียวกัน และ policy ที่เขียนถึงตัวหนึ่งจะไปคุมอีกตัว

**ข้อ 3 เป็นของที่ผู้รายงานยังไม่ได้ครอบ** — `2fa_setup` เติม namespace แล้ว segment ท้ายยังขึ้นต้นด้วยตัวเลข · การเดา prefix ให้จะทำให้ผลไม่ deterministic ซึ่งย้อนแย้งกับเหตุผลทั้งหมด

### รูปของบันทึก mapping ยังไม่สร้าง

`mcp/v1.exposes` จะเก็บชื่ออะไรเป็นคำถามที่ถูก — แต่**ยังไม่มีใคร pin `mcp/v1`** จึงเขียนกฎว่า *ต้องย้อนกลับได้* ไว้ก่อน ไม่เดารูป · เหตุผลเดียวกับที่ [ADR-0025](../../../decisions/0025-provider-switch-and-what-identity-covers.md) ไม่สร้าง field ให้ cost attribution

## v1.0.0 — 2026-08-17
- ตั้งต้นจาก `ref/enterprise-agent-backend-os-blueprint.md` §7
- `risk_level` → `action_risk` ตาม [ADR-0010](../../../decisions/0010-risk-approval-taxonomy.md)
- ถอด `approval_required` ออก — เป็นผลของ policy ไม่ใช่คุณสมบัติของ tool
