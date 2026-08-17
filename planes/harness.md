# Harness — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | `ai-web-harness` (web build, scaffold stage) · harness อื่นตามงาน |
| Contracts | `execution/v1` · `policy/v1` · `profile/v1` |
| ADR | [0005](../decisions/0005-agent-runtime-boundary.md) |

## Harness คืออะไร (และไม่ใช่อะไร)

**execution policy** — บังคับว่าขั้นตอนภายในหนึ่งงานต้องเดินตามลำดับไหน

```text
Intent → Permission → Retrieve → Reason → Tool → Verify → Cite/Audit
```

⚠️ คำว่า harness เคยถูกใช้เรียกของสองอย่าง — [ADR-0005](../decisions/0005-agent-runtime-boundary.md) แยกแล้ว:

| คำ | หมายถึง | อยู่ที่ |
| --- | --- | --- |
| **Harness** | execution policy | ไฟล์นี้ |
| **Evals** | สนามทดสอบ / scenario / evaluator | [`evals.md`](evals.md) |

`navi-security-agent` ที่เรียกโฟลเดอร์ `harness/scenarios/` ของตัวเองว่า harness — ตามศัพท์ที่ lock แล้วคือ **evals**

## รับผิดชอบ

* กำหนดลำดับขั้นบังคับต่อประเภทงาน — agent เลือกข้ามเองไม่ได้
* ตรวจ evidence ก่อนให้ผ่านไปขั้นถัดไป (เช่น ต้องมี citation ก่อนตอบ)
* ผูกกับ [`profiles/`](../profiles) — profile บอกว่าใช้ tool อะไรได้ harness บอกว่าใช้ตามลำดับไหน

## ห้ามทำ

* ตัดสิน governance — เรียก policy plane เอาผลมาใช้เท่านั้น
* จัดการงานข้าม request/ข้าม process — นั่นคือ [`workflow`](workflow.md) ซึ่งมี lifetime คนละแบบ

## เส้นแบ่ง

```text
Workflow   งานหลายขั้น หลาย agent · durable ข้าม process
    ↓
Harness    ลำดับขั้นภายในหนึ่งงาน · อยู่ใน lifetime ของ request
    ↓
Runtime    agent loop เดียว
    ↓
Sandbox    ที่ที่ command รันจริง
```

## สถานะ

`ai-web-harness` มีโครง `harness/workflow` + `harness/checks` แล้วแต่ยังเป็น scaffold · ยังไม่มี harness กลางที่ใช้ข้ามงาน
