# Knowledge — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | `enterprise-knowledge` — ยังไม่มี repo |
| Contracts | `tool/v1` (`knowledge.search`) · `identity/v1` · `policy/v1` |
| ADR | [0002](../decisions/0002-core-repository-naming.md) · [0007](../decisions/0007-multi-tenancy.md) |

## รับผิดชอบ

```text
Ingest → Parse → Classify → Chunk → Embed → Index → Retrieve → Feedback → Re-index
```

* connector: GitHub, Odoo, ฐานข้อมูล, ไฟล์, เว็บ, อีเมล, IoT
* hybrid retrieval — keyword + vector + graph แล้ว rerank ไม่ใช่ vector อย่างเดียว
* provenance: รู้ว่าความรู้มาจากไหน ใครสร้าง เมื่อไร version ไหน
* citation ที่ตรวจสอบย้อนได้

## ห้ามทำ

* **retrieval ที่ไม่ enforce ACL** — ความเสี่ยงหลักของ plane นี้ไม่ใช่ทำข้อมูลพัง แต่คือ *เห็นสิ่งที่ไม่ควรเห็น*
* ข้าม tenant boundary ไม่ว่ากรณีใด ([ADR-0007](../decisions/0007-multi-tenancy.md))
* กลายเป็น RAG แยกที่มี identity/policy ของตัวเอง — ต้องใช้ของ platform

## เข้าถึงผ่าน tool ไม่ใช่ API พิเศษ

agent เรียก `knowledge.search` เหมือน tool ทั่วไป จึงถูก policy ตรวจด้วยกลไกเดียวกัน — ไม่มีทางลัด

## ชื่อที่เลิกใช้

`enterprise-agent-knowledge-platform` → **`enterprise-knowledge`** · `enterprise-rag` เป็น module ข้างในไม่ใช่ repo แยก ([ADR-0002](../decisions/0002-core-repository-naming.md))

## สถานะ

ยังไม่มี repo · [`profiles/knowledge-agent`](../profiles/knowledge-agent/profile.yaml) กำหนดกรอบอำนาจไว้แล้ว (อ่านอย่างเดียว)
