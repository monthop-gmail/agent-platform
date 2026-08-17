# Gateway — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | `agent-gateway` — ยังไม่มี repo |
| Contracts | `identity/v1` · `policy/v1` · `capability/v1` · `tool/v1` |
| ADR | [0003](../decisions/0003-agent-gateway-boundary.md) |

## ทิศทางที่ plane นี้รับผิดชอบ

**inbound เท่านั้น** — agent ภายนอก (Claude Code, Codex, ระบบของลูกค้า) เข้ามาหา enterprise backend

อีกสองทิศทางเป็นคนละระบบ ไม่ใช่ plane นี้ ([ADR-0003](../decisions/0003-agent-gateway-boundary.md)):

| ทิศทาง | ระบบ |
| --- | --- |
| outbound — เราไปเรียก provider | `model-gateway` |
| fan-out — สั่งงาน worker หลัง NAT | `agent-fleet` |

⚠️ ห้ามใช้คำว่า "gateway" เดี่ยว ๆ ในเอกสารหรือ contract — ต้องระบุว่าตัวไหน

## รับผิดชอบ

```text
Authentication → Tenant Resolution → Agent Identity → Authorization
→ Tool Discovery → Policy Check → Approval → Execution → Audit
```

* ตรวจตัวตนและ resolve `tenant_id` / `workspace_id` ก่อนอย่างอื่นทั้งหมด
* เรียก policy plane และบังคับผลของมัน — ไม่ตีความเอง
* trigger approval flow เมื่อ policy ตอบ `approval_required`
* rate limit, quota, budget enforcement
* normalize request/response ให้ตรง contract
* ปล่อย audit event ทุกครั้ง ไม่ว่าผลจะเป็นอย่างไร

## ห้ามทำ

* ตัดสินใจแทน agent ว่าจะทำอะไรต่อ
* เก็บ business state (นั่นคือหน้าที่ของ backend-os)
* เรียก model เอง — ต้องผ่าน runtime
* ปล่อยให้ agent เข้าถึง backend resource ตรง ๆ ไม่ว่ากรณีใด

## เส้นแบ่ง

`Gateway` ตรวจว่า **ใครทำอะไรได้** · `Runtime` ตัดสิน **จะทำอะไรต่อ** · `Adapter` แปลง protocol เท่านั้น

## สถานะ

ยังไม่มี implementation · **`contracts/gateway/` ยังไม่ได้เขียน** — ไม่อยู่ในลิสต์ P0 ที่ตกลงไว้ ถ้าจะเพิ่มต้องผ่าน [issue contract-change](https://github.com/monthop-gmail/agent-platform/issues/new/choose)
