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
* **ข้าม workspace โดยไม่มีการตัดสินที่บันทึกไว้** ([ADR-0021](../decisions/0021-workspace-is-a-scope-not-a-boundary.md)) — ต่างจาก tenant ตรงที่ *มีคนอนุญาตให้ข้ามได้* ไม่ใช่ตรงที่เข้มน้อยกว่า
* กลายเป็น RAG แยกที่มี identity/policy ของตัวเอง — ต้องใช้ของ platform

## ขอบเขตของการค้น

knowledge อยู่ **ใน workspace** ไม่ใช่ลอยอยู่ใน tenant ([ADR-0007](../decisions/0007-multi-tenancy.md) · [ADR-0021](../decisions/0021-workspace-is-a-scope-not-a-boundary.md))

| ชั้น | บังคับที่ไหน | ข้ามได้ไหม |
| --- | --- | --- |
| `tenant_id` | **ชั้นเก็บข้อมูล** — RLS · partition · index | ไม่ได้ทุกกรณี · โค้ดเขียนผิดก็ยังข้ามไม่ได้ |
| `workspace_id` | **ชั้นตรวจสิทธิ์** — scope โดยปริยายทุก query | ได้ ถ้ามีการตัดสินจาก [`policy/v1`](../contracts/policy/v1/) และ **บันทึกไว้ทุกครั้ง** |

`Project` และ `Department` เป็น **label ของ workspace** ไม่ใช่ชั้น id ใหม่ · **metadata filter ที่ลอยอยู่โดยไม่มี workspace คือชั้นที่สามที่ ADR-0007 ห้ามไว้ ในชื่ออื่น**

## เข้าถึงผ่าน tool ไม่ใช่ API พิเศษ

agent เรียก `knowledge.search` เหมือน tool ทั่วไป จึงถูก policy ตรวจด้วยกลไกเดียวกัน — ไม่มีทางลัด

## ชื่อที่เลิกใช้

`enterprise-agent-knowledge-platform` → **`enterprise-knowledge`** · `enterprise-rag` เป็น module ข้างในไม่ใช่ repo แยก ([ADR-0002](../decisions/0002-core-repository-naming.md))

## สถานะ

ยังไม่มี repo · [`profiles/knowledge-agent`](../profiles/knowledge-agent/profile.yaml) กำหนดกรอบอำนาจไว้แล้ว (อ่านอย่างเดียว)
