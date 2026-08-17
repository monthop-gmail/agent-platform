# Workflow — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | ยังไม่มี repo · `devfactory-core/packages/orchestrator` เป็นของฝั่ง job |
| Contracts | [`execution/v1`](../contracts/execution/v1/) · `policy/v1` · `profile/v1` |
| ADR | [0005](../decisions/0005-agent-runtime-boundary.md) · อิง `devfactory-core` RFC-0004 |

## รับผิดชอบ (orchestration)

จาก RFC-0004 ซึ่ง [extraction §1](../architecture/devfactory-core-rfc-extraction.md) สรุปว่ายกมาใช้ได้ทั้งดุ้น:

* task decomposition
* dependency resolution
* retry / timeout / schedule
* human-in-the-loop step
* fan-out / fan-in ผ่าน execution ลูกที่มี `parent_execution_id`

## ห้ามทำ

* **แก้ artifact เอง** (RFC-0004) — สั่งให้ execution ทำ ไม่ใช่ลงมือเอง
* ตัดสิน governance
* ให้ลูกมีสิทธิ์หรือ budget กว้างกว่าพ่อ

## สามระดับที่ต้องไม่สับสน

| ระดับ | เจ้าของ | ตัวอย่าง |
| --- | --- | --- |
| **Job** | `devfactory-core` RFC-0001 | "แก้ issue #123" |
| **Execution** | [`contracts/execution/v1`](../contracts/execution/v1/) | "รัน claude-code ใน worker-01" |
| **Step** | `contracts/event/` ⏳ | "เรียก github.pr.create" |

`job_id` ใน execution เป็น **optional** เพราะไม่ใช่ทุก execution เกิดจาก job — chat turn, retrieval และ observer event ไม่มี job

## เส้นแบ่งกับ Harness

`Workflow` durable ข้าม process อยู่ได้ข้ามวัน · [`Harness`](harness.md) อยู่ใน lifetime ของ request เดียว — รวมกันไม่ได้เพราะ lifetime คนละแบบ

## สถานะ

state machine ระดับ execution เขียนแล้วรวม retry semantics และ parallel substates (ตอบ open question ที่ RFC-0001 ทิ้งไว้) · orchestration engine ยังไม่มี implementation
