# ADR-0001: Platform Scope

**Status:** Proposed
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

repo เก็บ `contracts/` `architecture/` `decisions/` `profiles/` และ `modules/` ที่เป็นเอกสาร — ไม่มี runtime code, ไม่มี build, ไม่มี dependency manifest

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

## Decision

> _(รอเคาะ)_

## Consequences ถ้าเลือก A

* ต้องเขียน `CORE_BOUNDARY.md` ของ platform เอง ตามแบบ `devfactory-core`
* `modules/` 10 ตัวปัจจุบันเปลี่ยนสถานะเป็น "เอกสารขอบเขต" อย่างเป็นทางการ ไม่ใช่ที่รอ code
* implementation ทั้งหมดไปอยู่ repo ลูก → ต้องตอบ ADR-0002 ว่า repo ลูกชื่ออะไร
* ต้องมีกลไกกัน drift: repo ลูกต้องมี conformance test ที่อ้าง contract version (ADR-0006)

## Sources

* คำสั่งเจ้าของ repo 2026-08-17 · [`../ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) · [`../ref/agent-platform-decisions-first-plan.md`](../ref/agent-platform-decisions-first-plan.md)
* `devfactory-core/docs/governance/CORE_BOUNDARY.md` — ดู [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §5
