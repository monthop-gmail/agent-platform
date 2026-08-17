# ADR-0008: Reference Stack

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Depends on:** ADR-0001

## Context

`ref/` เสนอ stack ที่ต่างกัน **4 ชุด** สำหรับสิ่งที่อ้างว่าเป็น platform เดียวกัน:

| ที่มา | stack |
| --- | --- |
| [`backend-os §2, §18`](../ref/enterprise-agent-backend-os-blueprint.md) | Cloudflare — Workers · Durable Objects · D1 · R2 · KV · Queues · Workflows · AI Gateway |
| [`knowledge-platform §12`](../ref/enterprise-agent-knowledge-platform-blueprint.md) | Python/FastAPI · LlamaIndex · PostgreSQL · Qdrant · Neo4j · MinIO · Keycloak · OTel · APISIX |
| [`distributed-gateway`](../ref/distributed-multi-agent-gateway-blueprint.md) | Node/TypeScript **หรือ** FastAPI · SQLite WAL · MQTT/NATS |
| [`navi-security-agent §8`](../ref/navi-security-agent-blueprint.md) | Agent Runtime · FastAPI/Node · Event Bus · Redis · PostgreSQL · Vector store |

ของจริงที่รันอยู่แล้วก็คนละอย่าง: `navi-ims` = Odoo 19 + Celery + Inngest + MediaMTX (Python) · `ai-web-harness` = Astro (Node) · `devfactory-core` = ยังไม่มี code

ทุก blueprint ย้ำหลักเดียวกันคือ **ห้ามผูก vendor** — `backend-os §18` ถึงเสนอ `providers/{cloudflare,docker,kubernetes}` และ `naming-convention` สั่งไม่ให้ตั้งชื่อ repo ว่า `cloudflare-os-*`

และมีคำตอบอยู่แล้วในบ้าน: `devfactory-core/docs/governance/CORE_BOUNDARY.md` อนุญาต *"เพิ่ม interface / contract (**ไม่ผูก tech**)"* และห้าม *"เพิ่ม framework ที่ผูก vendor"*

## Options

### A. Contract เป็น tech-neutral · แต่ละ implementation repo เลือก stack เอง (แนะนำ)

* `contracts/` เขียนด้วย **YAML / JSON Schema** เท่านั้น — ไม่มี TypeScript type, ไม่มี Pydantic model, ไม่มี proto ใน repo นี้
* code generation เป็นหน้าที่ repo ลูก (แต่ละภาษา gen จาก schema เดียวกัน)
* ADR นี้ **ไม่บังคับ** stack ให้ repo ลูก แต่บันทึกว่าใครใช้อะไรใน `architecture/`
* Cloudflare / Docker / k8s เป็น **provider ของ `agent-backend-os`** ไม่ใช่ของ platform

* ✅ ตรงกับ ADR-0001 option A และ CORE_BOUNDARY ของ devfactory-core
* ✅ ไม่ต้องเลือกระหว่าง Cloudflare กับ Python — ทั้งสองเป็น implementation ที่ถูกทั้งคู่ในบริบทต่างกัน
* ✅ ของที่รันอยู่แล้ว (Odoo, Astro) ไม่ต้องย้าย
* ❌ schema-only ทำให้ DX แย่กว่า typed SDK → แก้ด้วย codegen ใน repo ลูก (ไม่ใช่ repo นี้)

### B. เลือก stack กลางหนึ่งชุดให้ทั้ง ecosystem

* ✅ DX ดีที่สุด แชร์ library ได้
* ❌ ขัดหลัก "ไม่ผูก vendor" ที่ 4 blueprint ย้ำ
* ❌ ต้องย้าย `navi-ims` (Odoo/Python) หรือ `ai-web-harness` (Astro) ตัวใดตัวหนึ่ง — ต้นทุนจริงโดยไม่ได้ประโยชน์เพิ่ม
* ❌ ขัด ADR-0001 option A (repo ที่ไม่ implement ไม่ควรบังคับ stack)

### C. เลือก reference stack สำหรับ PoC/example เท่านั้น (ไม่บังคับ production)

* ✅ มี stack เดียวให้เขียน example และ conformance test
* ⚠️ ถ้าเลือกทางนี้ เกณฑ์ควรเป็น **`docker compose up` ต้องรันได้ทันที** ซึ่งเป็นข้อกำหนดที่ 3 blueprint เห็นตรงกัน (knowledge §12 "อย่าเริ่ม Kubernetes ก่อน" · distributed-gateway DoD · navi Phase 0)
* ⚠️ ต้องระวังว่า example จะโตเป็น implementation — ผูกกับเพดานใน ADR-0001

## Decision

**A** — contract เป็น **tech-neutral** (YAML / JSON Schema เท่านั้น) · implementation repo เลือก stack เอง · codegen เป็นหน้าที่ repo ลูก

**Reason:** ecosystem มี Cloudflare, Python, Node, Odoo, Astro อยู่แล้ว การบังคับ stack กลางเป็นภาระโดยไม่ได้ประโยชน์เพิ่ม และต้องย้ายของที่รันอยู่จริง · ตรงกับ `devfactory-core/docs/governance/CORE_BOUNDARY.md` ที่อนุญาต "เพิ่ม interface / contract (ไม่ผูก tech)" และห้าม framework ที่ผูก vendor · Cloudflare ยังใช้ได้เต็มที่ในฐานะ provider ตัวหนึ่งของ `agent-backend-os` ไม่ใช่ของ platform

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

ห้ามมีใน repo นี้: `package.json` · `pyproject.toml` · `Dockerfile` · `docker-compose.yml` · lockfile · typed SDK ทุกภาษา

## Consequences ถ้าเลือก A

* `contracts/` มีแต่ `.yaml` / `.json` — ห้ามมี `package.json`, `pyproject.toml`, `Dockerfile` ใน repo นี้
* เขียน `architecture/stack-inventory.md` บันทึกว่า repo ไหนใช้ stack อะไร (เพื่อรู้ว่า codegen ต้องรองรับภาษาอะไร)
* ข้อกำหนด `docker compose up` ยังอยู่ แต่เป็นข้อกำหนดของ **repo ลูก** ไม่ใช่ของ platform
* Cloudflare ยังใช้ได้เต็มที่ — แต่ในฐานะ provider ตัวหนึ่งใน `agent-backend-os/providers/cloudflare` ตาม backend-os §18

## หมายเหตุลำดับ

ADR นี้ **urgent น้อยที่สุดในชุด 8 ตัว** ถ้า ADR-0001 = A เพราะ repo ที่ไม่ implement ไม่ต้องเลือก stack — แต่ต้องเคาะก่อนเริ่มเขียน `contracts/` เพื่อไม่ให้มีใครเผลอ commit typed SDK ลง repo นี้

## Sources

[`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §2, §18 · [`../ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §12 · [`../ref/distributed-multi-agent-gateway-blueprint.md`](../ref/distributed-multi-agent-gateway-blueprint.md) · [`../ref/naming-convention-ecosystem.md`](../ref/naming-convention-ecosystem.md) · `devfactory-core/docs/governance/CORE_BOUNDARY.md`
