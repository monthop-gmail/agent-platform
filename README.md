# agent-platform

> **Agent Platform is the unified foundation for building, connecting, operating, governing, and scaling AI agents across enterprise applications.**

ชื่อนี้ไม่ผูก vendor, ไม่ผูก Cloudflare และไม่จำกัดตัวเองไว้แค่ backend — repo นี้เป็น **core platform** ที่ product/application repo อื่น ๆ มา consume

## ⚠️ repo นี้ไม่ implement

repo นี้มีหน้าที่ **คุมภาพรวมและปรับปรุงโครง module** เท่านั้น — เก็บ architecture, module boundary, contract และ decision record

**code จริงอยู่ใน product/application repo** ที่ consume platform นี้ (ดู [Ecosystem](#ecosystem))
ถ้าจะเพิ่ม service, build tooling หรือ implementation ใด ๆ ให้ไปที่ repo ปลายทาง ไม่ใช่ที่นี่

## โฟลเดอร์ไหนเก็บอะไร

| โฟลเดอร์ | เนื้อหา | ผลผูกพัน |
| --- | --- | --- |
| [`decisions/`](./decisions) | ADR ระดับ ecosystem — ศัพท์และขอบเขตที่ตกลงกันแล้ว | ✅ ผูกพัน |
| [`architecture/`](./architecture) | คำอธิบาย, mapping, ผลวิเคราะห์ repo อื่น | 📄 อธิบาย |
| [`ref/`](./ref) | บันทึกดิบตามเวลา ขัดกันเองได้ | ❌ ไม่ผูกพัน |
| module dirs ด้านล่าง | นิยามขอบเขตของแต่ละ plane | 📄 อธิบาย |

`contracts/` (canonical schema) ยังไม่สร้าง — รอ [vocabulary gate](./decisions#ลำดับที่ควรเคาะ) ผ่านก่อน

## Modules

แต่ละ directory เก็บ **นิยามขอบเขต** ของ module นั้น ไม่ใช่ code

| Module | หน้าที่ |
| --- | --- |
| [`backend-os`](./backend-os) | ชั้น OS ของ backend — core services, data plane, integration กับ enterprise system |
| [`agent-gateway`](./agent-gateway) | ทางเข้าเดียวของทุก agent traffic — auth, routing, rate limit, quota |
| [`agent-runtime`](./agent-runtime) | ที่ agent รันจริง — loop, state, memory, lifecycle |
| [`agent-harness`](./agent-harness) | harness สำหรับ test / eval / benchmark agent |
| [`tool-registry`](./tool-registry) | catalog ของ tool ที่ agent เรียกได้ พร้อม schema และ versioning |
| [`policy-engine`](./policy-engine) | governance — permission, guardrail, approval, audit rule |
| [`knowledge`](./knowledge) | ingestion, index และ retrieval ของ enterprise knowledge |
| [`workflow`](./workflow) | orchestration ของงานหลายขั้น / หลาย agent |
| [`sandbox`](./sandbox) | execution environment ที่ isolate สำหรับ code และ tool ที่ไม่น่าเชื่อถือ |
| [`observability`](./observability) | trace, metric, log, cost และ replay ของทุก agent run |

## Architecture

ภาพย่อระดับ ecosystem — ภาพเต็มที่แสดง capability routing และการแยก provider สองชั้นอยู่ที่ [`architecture/platform-architecture.md`](./architecture/platform-architecture.md)

```text
                  agent-platform
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
  Agent Gateway     Agent Runtime    Knowledge
       │                │                │
       └────────────────┼────────────────┘
                        │
                Enterprise Backend
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
      Odoo            IoT/VMS         GitHub
```

## Ecosystem

repo นี้เป็น core — repo อื่นเป็น products/applications ที่ consume platform นี้ ไม่ใช่คู่แข่งกันเอง

```text
monthop-gmail/
│
├── agent-platform          ⭐ CORE
│
├── devfactory-core         Product
├── ai-web-harness          Harness
├── navi-ims                Product
├── navi-security-agent     Agent
├── enterprise-knowledge    Knowledge
├── odoo-farm               Application
└── farm-agent              Agent
```

## Status

🔒 **VOCABULARY LOCKED — 2026-08-17** · ADR ทั้งหมด `Accepted` แล้ว ดู [`decisions/`](./decisions)

ยกเว้นข้อเดียว: **ADR-0006 ownership** ยัง `Pending` — `agent-platform` ยังไม่ใช่ canonical owner ของ shared contract จนกว่า Architecture Owner ของ [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) จะยืนยัน ([issue #6](https://github.com/monthop-gmail/agent-platform/issues/6))

**ขั้นตอนปัจจุบัน:** `contracts/` P0 — contract ที่ไม่อ้าง RFC ของ `devfactory-core` เริ่มได้เลย · contract ที่อ้าง (`approval/`, `event/`) ติดสถานะ `external-authority-pending`

ถัดไป: `profiles/` → ย้าย module ตาม [module mapping](./architecture/module-mapping.md)

การสื่อสารข้ามทีมใช้ GitHub: **issue** สำหรับเคาะ ADR และขอแก้ contract · **PR** สำหรับรีวิว (comment ที่บรรทัด ไม่ใช่เขียนเรียงความ) · **milestone** สำหรับดูว่าติดเฟสไหน

## Reference

- [`decisions/`](./decisions) — ADR ทั้งหมดและลำดับที่ควรเคาะ
- [`architecture/platform-architecture.md`](./architecture/platform-architecture.md) — canonical diagram (`Proposed`) พร้อมกำกับว่าชั้นไหนรอ ADR ตัวไหน
- [`architecture/consumers.md`](./architecture/consumers.md) — ทะเบียน consumer และสถานะ conformance
- [`architecture/module-mapping.md`](./architecture/module-mapping.md) — module ปัจจุบัน → โครงเป้าหมาย (ยังไม่ย้าย)
- [`architecture/devfactory-core-rfc-extraction.md`](./architecture/devfactory-core-rfc-extraction.md) — ดึง RFC ของ `devfactory-core` มาเป็น canonical contract อะไรได้แค่ไหน
- [`ref/`](./ref) — บันทึกดิบ พร้อมสารบัญและตารางข้อขัดแย้งที่รู้แล้ว
- [`ref/existing-repos.md`](./ref/existing-repos.md) — inventory ของ repo ที่มีอยู่จริง

## License

[MIT](./LICENSE)
