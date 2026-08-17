# Runtime — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | native runtime → `agent-backend-os` · external → agent provider (Claude Code, Codex, OpenCode, Hermes) |
| Contracts | [`execution/v1`](../contracts/execution/v1/) · `agent/v1` · `capability/v1` · `identity/v1` |
| ADR | [0005](../decisions/0005-agent-runtime-boundary.md) option C2 |

## สองเส้นทางใต้ contract เดียว

```text
contracts/execution/v1
        │
   ┌────┴─────────────────────┐
   ▼                          ▼
native runtime          external agent provider
(agent-backend-os)      (Claude Code / OpenCode / Hermes / Codex)
```

`execution_mode: native | provider` เป็นตัวบอกว่างานนี้เดินทางไหน — **agent ที่ทีมเขียนเองต้องไม่เป็น citizen ชั้นสอง** จึงไม่บังคับให้แพ็กตัวเองเป็น provider

## รับผิดชอบ

* agent loop — ตัดสินว่ารอบถัดไปทำอะไร (เฉพาะ native · external provider ทำเอง)
* session / state / context assembly
* แปลง tool call เป็น action แล้วส่งผ่าน gateway
* lifecycle: spawn / resume / cancel / timeout
* รายงาน usage และ artifact กลับตาม contract

ความเป็นเจ้าของแต่ละส่วนต่างกันตามเส้นทาง — ดูตารางใน [ADR-0005](../decisions/0005-agent-runtime-boundary.md)

## ห้ามทำ

จาก `devfactory-core` RFC-0004 · [ADR-0003](../decisions/0003-agent-gateway-boundary.md) · [ADR-0005](../decisions/0005-agent-runtime-boundary.md):

* **ตัดสิน governance เอง** — execution ไม่มีอำนาจอนุมัติตัวเอง
* **แตะ backend resource ตรง ๆ** — ต้องผ่าน gateway เสมอ
* **ถือ provider credential เอง**

external provider ก็อยู่ใต้กฎเดียวกัน ไม่มีสิทธิ์พิเศษเพราะเป็นของ vendor

## สิ่งที่ contract ต้องรับมือ

external provider มองไม่เห็น step ข้างในตัวเอง → `observability_depth: turn` เป็นเรื่องปกติ **ห้ามตีความว่า execution ที่ไม่มี step คือ execution ที่ไม่ได้ทำอะไร**

## สถานะ

contract เขียนแล้ว ([`execution/v1`](../contracts/execution/v1/)) รวม state machine, retry semantics และ parallel substates · native runtime ยังไม่มี repo
