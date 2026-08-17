# ADR-0001: Platform Scope

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Blocking:** ADR ทุกตัวที่เหลือ + `contracts/` ทั้งหมด

## Context

`agent-platform` ถูกสร้างเป็น core repo ของ ecosystem โดยเจ้าของ repo ระบุไว้ตั้งแต่ต้นว่า **"จะไม่ implement จะเอาไว้คุมภาพรวมและปรับปรุงโครง module"**

แต่เอกสารใน `ref/` เสนอโครงที่ขัดกับข้อนั้น:

| ที่มา | เสนอให้ core repo เป็น |
| --- | --- |
| คำสั่งเจ้าของ repo + README ปัจจุบัน | architecture/docs เท่านั้น ไม่มี code |
| [`ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §3 | mono-repo มี code: `apps/{gateway,api,dashboard,agent-runtime}` + `packages/` 11 ตัว |
| [`ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §13 | mono-repo มี code: `apps/` + `core/` + `adapters/` + `connectors/` |
| [`ref/naming-convention-ecosystem.md`](../ref/naming-convention-ecosystem.md) | multi-repo — module แต่ละตัวเป็น repo แยก |
| [`ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) | contract repository ไม่ implement |
| [`ref/agent-platform-decisions-first-plan.md`](../ref/agent-platform-decisions-first-plan.md) | "รัฐธรรมนูญของ Agent Ecosystem" ไม่ implement |

ปัจจุบัน repo มี 10 directory ที่มีแค่ README ระบุ scope — ยังไม่มี code

มีตัวอย่างจริงในบ้านแล้ว: `devfactory-core` ประกาศ boundary ของตัวเองใน `docs/governance/CORE_BOUNDARY.md` ว่า v0.x ทำได้แค่ RFC / skeleton / **interface-contract ที่ไม่ผูก tech** / diagram / test logic และห้าม vendor framework, UI, auto-deploy

## Options

### A. Contract & architecture only (แนะนำ)

repo เก็บ `contracts/` `architecture/` `decisions/` `profiles/` และโฟลเดอร์เอกสารขอบเขต — ไม่มี runtime code, ไม่มี build, ไม่มี dependency manifest

* ✅ ตรงกับคำสั่งเจ้าของ repo และ ref 2 ฉบับล่าสุด
* ✅ contract เปลี่ยนช้ากว่า code → repo นิ่ง ทำหน้าที่ authority ได้
* ✅ มี precedent ในบ้าน (`devfactory-core` CORE_BOUNDARY)
* ❌ contract ที่ไม่มี reference implementation อาจ drift จากความจริง → แก้ด้วย conformance test ใน repo ลูก

### B. Mono-repo ที่มี code ทุก module

ตาม backend-os blueprint §3 / knowledge blueprint §13

* ✅ contract กับ implementation อยู่ที่เดียว drift ยาก
* ❌ ขัดคำสั่งเจ้าของ repo โดยตรง
* ❌ ต้องเลือก stack ทันที (ADR-0008) และล็อกทั้ง ecosystem ไว้กับมัน
* ❌ repo กลายเป็น bottleneck — ทุกทีมต้อง PR เข้าที่เดียว

### C. Hybrid — contract + reference implementation ขนาดเล็ก

เพิ่ม `examples/` หรือ `conformance/` ที่รันได้ แต่ไม่ใช่ production service

* ✅ พิสูจน์ว่า contract ใช้ได้จริง
* ❌ เส้นแบ่ง "เล็ก" ไม่ชัด มีโอกาสโตเป็น B โดยไม่มีใครสังเกต
* ⚠️ ถ้าเลือกทางนี้ต้องเขียน CORE_BOUNDARY ที่ระบุเพดานเป็นตัวเลข (เช่น ห้ามมี service, ห้ามมี DB, ห้ามมี CI deploy)

## Options — ชื่อโฟลเดอร์เอกสารขอบเขต

10 directory ปัจจุบันจะกลายเป็นเอกสารทั้งหมด ต้องตั้งชื่อโฟลเดอร์ให้คนใหม่ไม่ถามว่า *"ทำไมมีแต่ markdown?"*

### A2. `planes/` (แนะนำ)

```text
planes/
├── gateway.md
├── runtime.md
├── knowledge.md
└── ...
```

* ✅ ชื่อบอกเองว่าเป็น **ขอบเขตของ plane** ไม่ใช่ที่เก็บ code — ไม่ต้องพึ่ง README มาอธิบาย
* ✅ ตรงกับศัพท์ที่ `devfactory-core` ใช้อยู่แล้ว (Control / Orchestration / Execution / Observability plane)
* ❌ ต่างจากคำว่า `modules/` ที่ [`ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) เสนอไว้

### B2. `modules/` + ประกาศนิยามชัดใน README

* ✅ ตรงกับที่ ref เสนอ ทีมที่อ่าน review มาแล้วจำได้
* ❌ คำว่า module สื่อถึง code unit โดยธรรมชาติ → ต้องอธิบายทุกครั้งที่มีคนใหม่เข้ามา

**ไม่ว่าจะเลือกชื่อไหน นิยามต้องเป็นข้อเดียวกัน:**

> โฟลเดอร์นี้คือ **Plane Boundary Documentation** — เอกสารระบุขอบเขต ความรับผิดชอบ และสิ่งที่ห้ามทำของแต่ละ plane
> **ไม่ใช่** ที่เก็บ implementation และ **ไม่ใช่** ที่รอ code มาลง
> code ของ plane นั้นอยู่ใน repo ลูกที่ระบุไว้ในหัวไฟล์

## Decision

**A + A2** — `agent-platform` เป็น **Contract & Architecture authority** ไม่มี implementation · โฟลเดอร์เอกสารขอบเขตใช้ชื่อ **`planes/`** ในความหมาย **Plane Boundary Documentation**

**Reason:** ตรงกับ intent เดิมของเจ้าของ repo และมี precedent ในบ้านแล้วที่ `devfactory-core/docs/governance/CORE_BOUNDARY.md` ซึ่งจำกัดตัวเองไว้ที่ RFC / skeleton / interface-contract ที่ไม่ผูก tech · เลือก `planes/` แทน `modules/` เพราะชื่อบอกความหมายตัวเองว่าเป็นขอบเขต ไม่ใช่ที่เก็บ code จึงไม่ต้องอธิบายซ้ำทุกครั้งที่มีคนใหม่เข้ามา และตรงกับศัพท์ plane ที่ `devfactory-core` ใช้อยู่แล้ว · ปฏิเสธ B เพราะทำให้ repo เป็น bottleneck และต้องล็อก stack ทันที ปฏิเสธ C เพราะเส้นแบ่ง "reference implementation ขนาดเล็ก" ไม่ชัดพอที่จะกันไม่ให้โตเป็น B

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

## Consequences ถ้าเลือก A

* ต้องเขียน `CORE_BOUNDARY.md` ของ platform เอง ตามแบบ `devfactory-core`
* 10 directory ปัจจุบันเปลี่ยนสถานะเป็น **Plane Boundary Documentation** อย่างเป็นทางการ ไม่ใช่ที่รอ code — ทุกไฟล์ต้องระบุที่หัวว่า *"implementation อยู่ที่ repo ไหน"*
* implementation ทั้งหมดไปอยู่ repo ลูก → ต้องตอบ ADR-0002 ว่า repo ลูกชื่ออะไร
* ต้องมีกลไกกัน drift: repo ลูกต้องมี conformance test ที่อ้าง contract version — เป็น **ข้อบังคับ** ไม่ใช่ข้อแนะนำ ดู [ADR-0006](0006-contract-versioning.md)
* ห้ามมีไฟล์เหล่านี้ใน repo: `package.json` · `pyproject.toml` · `Dockerfile` · `docker-compose.yml` · lockfile ([ADR-0008](0008-reference-stack.md))

## Sources

* คำสั่งเจ้าของ repo 2026-08-17 · [`../ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) · [`../ref/agent-platform-decisions-first-plan.md`](../ref/agent-platform-decisions-first-plan.md)
* `devfactory-core/docs/governance/CORE_BOUNDARY.md` — ดู [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §5
