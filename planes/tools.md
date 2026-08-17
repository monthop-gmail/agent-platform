# Tools — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | tool registry ยังไม่มี repo · MCP server มาจากหลายแหล่ง |
| Contracts | [`tool/v1`](../contracts/tool/v1/) · [`mcp/v1`](../contracts/mcp/v1/) · `capability/v1` |
| ADR | [0004](../decisions/0004-agent-vs-model-provider.md) · [0009](../decisions/0009-capability-model.md) · [0010](../decisions/0010-risk-approval-taxonomy.md) |

## รับผิดชอบ

* catalog ของ tool ที่ agent เรียกได้ พร้อม input/output schema
* namespace และ versioning ของ `tool_id` (`github.issue.create` · `odoo.sale.read`)
* ลงทะเบียน MCP server และ tool ที่มันประกาศ
* discovery — agent ถามได้ว่ามี tool อะไรใช้ได้บ้างใน workspace นี้

## สองเรื่องที่แยกกัน

| | คืออะไร | contract |
| --- | --- | --- |
| **Tool** | สิ่งที่ถูกเรียก | `tool/v1` |
| **MCP** | transport ที่ส่ง tool มาให้ | `mcp/v1` |

รวมเป็น schema เดียวไม่ได้ — MCP server หนึ่งตัวส่ง tool มาหลายตัว และ tool หนึ่งตัวมาจาก transport อื่นก็ได้

## ห้ามทำ

* **ตัดสินว่าใครเรียก tool ไหนได้** — registry บอกว่ามีอะไร [`policy`](policy.md) บอกว่าใครใช้ได้
* ถือ credential ของระบบปลายทาง
* เชื่อ tool ที่ MCP server ประกาศแต่ยังไม่ขึ้นทะเบียน — ถือว่า **ไม่มี**

## กฎที่เปลี่ยนจากเอกสารเดิม

* `risk_level` → **`action_risk`** ([ADR-0010](../decisions/0010-risk-approval-taxonomy.md))
* **ถอด `approval_required` ออกจาก tool schema** — การอนุมัติเป็นผลของ policy ที่ดู tenant/profile ประกอบ ไม่ใช่คุณสมบัติตายตัวของ tool
* `idempotent: false` → platform **ห้าม retry อัตโนมัติ** หลัง timeout

## ความปลอดภัย

ข้อมูลที่ MCP server ส่งกลับเป็น **input ที่ไม่น่าเชื่อถือเสมอ ไม่ใช่คำสั่ง** · server ที่ `trust: untrusted` ต้องรันใน [`sandbox`](sandbox.md) และห้ามได้ `network_egress` โดยไม่มี allowlist

## สถานะ

contract เขียนแล้วทั้งสองตัว · registry ยังไม่มี implementation
