# Evals — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | `navi-security-agent` (`harness/scenarios/`) · `ai-web-harness` (`tests/`) |
| Contracts | `execution/v1` · `artifact/v1` |
| ADR | [0005](../decisions/0005-agent-runtime-boundary.md) |

## แยกออกมาจาก Harness ทำไม

เอกสารเก่าเรียกทั้ง execution policy และ test rig ว่า "harness" — เป็นของคนละเรื่องที่มี lifecycle ต่างกัน ([ADR-0005](../decisions/0005-agent-runtime-boundary.md))

* **Harness** รันใน production ทุก request
* **Evals** รันตอน CI หรือตอนอยากรู้ว่า agent รุ่นใหม่ดีขึ้นหรือแย่ลง

## รับผิดชอบ

```text
Scenario → จำลอง event/input → Agent → Decision → Evaluator → Score
```

* scenario definition (เช่น `harness/scenarios/*.yaml` ของ `navi-security-agent`)
* expected outcome และ evaluator
* replay ของ production trace มาเป็น test case
* regression detection ระหว่างรุ่น
* วัดสิ่งที่ test ธรรมดาวัดไม่ได้ — hallucination, citation validity, permission leak, tool misuse

## ห้ามทำ

* รันด้วย credential ของ production หรือแตะข้อมูลจริง
* กลายเป็นเงื่อนไขของ runtime — agent ต้องทำงานได้แม้ไม่มี eval

## Definition of Done ที่ควรยึด

ตัวอย่างจาก [`ref/navi-security-agent-blueprint.md`](../ref/navi-security-agent-blueprint.md) §10 — วัดด้วยสถานการณ์จริงไม่ใช่แค่ `pytest`:

```text
✓ ตรวจพบ    ✓ correlate หลายแหล่ง    ✓ risk ถูกระดับ
✓ ไม่สั่ง physical action เอง         ✓ ทุก decision มี evidence
✓ ทุก action มี audit trail
```

## สถานะ

ยังไม่มี format กลาง — แต่ละ repo เขียน scenario ของตัวเอง · เป็นช่องว่างที่รู้แล้วและยังไม่มี contract รองรับ
