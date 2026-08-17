# Sandbox — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | ยังไม่มี repo · เป็นส่วนหนึ่งของ execution plane |
| Contracts | `capability/v1` (host scope) · `execution/v1` · `artifact/v1` |
| ADR | [0005](../decisions/0005-agent-runtime-boundary.md) · [0009](../decisions/0009-capability-model.md) |

## รับผิดชอบ

ที่ที่ command, code และ tool ที่ไม่น่าเชื่อถือรันจริง

* isolation — container / microVM / process jail
* resource limit: CPU, memory, disk, เวลา
* network policy — egress ต้องเป็น allowlist ไม่ใช่ deny-list
* filesystem isolation และ cleanup หลังจบงาน
* PTY handling สำหรับ CLI ที่ interactive · ตัด ANSI · จำกัดขนาด log

## capability ที่ประกาศจาก plane นี้

เป็น **host scope** ตาม [ADR-0009](../decisions/0009-capability-model.md) — คนละชั้นกับ capability ของ provider

```text
docker · network_egress · filesystem · shell
```

worker ประกาศผ่าน `capability/v1/declaration` แล้ว router ใช้เลือกว่างานนี้ลงเครื่องไหนได้

## ห้ามทำ

* รัน MCP server ที่ `trust: untrusted` นอก sandbox
* ให้ `network_egress` โดยไม่มี allowlist
* ส่ง credential เข้าไปใน sandbox ผ่าน task payload — ต้องเป็น reference ไปยัง secret store
* ปล่อย process ค้างหลัง execution เข้าสถานะ terminal

## เส้นแบ่ง

[`Runtime`](runtime.md) ตัดสินว่าจะรันอะไร · Sandbox คือที่ที่มันรัน — sandbox ไม่ตัดสินใจอะไรทั้งสิ้น

## สถานะ

ยังไม่มี implementation · เป็น plane ที่ `agent-fleet` (worker fan-out) ต้องพึ่งโดยตรง
