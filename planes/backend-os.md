# Backend OS — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | `agent-backend-os` — ยังไม่มี repo |
| Contracts | `identity/v1` · `execution/v1` · `artifact/v1` |
| ADR | [0002](../decisions/0002-core-repository-naming.md) · [0005](../decisions/0005-agent-runtime-boundary.md) · [0008](../decisions/0008-reference-stack.md) |

## รับผิดชอบ

* core service และ data plane ของ enterprise backend
* connector ไปยัง system of record — Odoo, IoT/VMS, GitHub, ฐานข้อมูล
* job queue, scheduler, transactional boundary
* **บ้านของ native runtime** ตาม [ADR-0005 C2](../decisions/0005-agent-runtime-boundary.md) — native runtime ไม่ได้อยู่ใน `agent-platform`

## ไม่ผูก vendor

Cloudflare (Workers / Durable Objects / D1 / R2) เป็น **provider ตัวหนึ่ง** ไม่ใช่ข้อบังคับ ([ADR-0008](../decisions/0008-reference-stack.md)):

```text
agent-backend-os/providers/
├── cloudflare/
├── docker/
└── kubernetes/
```

`ref/enterprise-agent-backend-os-blueprint.md` เขียนไว้บน Cloudflare — อ่านเป็น **หนึ่งทางเลือก implementation** ไม่ใช่คำสั่ง

## ห้ามทำ

* เปิดทางให้ agent เข้าถึง resource ตรงโดยไม่ผ่าน [`gateway`](gateway.md)
* ตัดสิน governance เอง — เรียก [`policy`](policy.md)
* กลายเป็นที่รวมทุกอย่างจนแยก plane ไม่ออก

## ชื่อที่เลิกใช้

`enterprise-agent-backend` → **`agent-backend-os`** ([ADR-0002](../decisions/0002-core-repository-naming.md))

## สถานะ

ยังไม่มี repo · เป็น plane ที่ blocking ตัวอื่นมากที่สุดเพราะเป็นทั้ง data plane และบ้านของ native runtime
