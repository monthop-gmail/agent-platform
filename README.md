# agent-platform

> **Agent Platform is the unified foundation for building, connecting, operating, governing, and scaling AI agents across enterprise applications.**

ชื่อนี้ไม่ผูก vendor, ไม่ผูก Cloudflare และไม่จำกัดตัวเองไว้แค่ backend — repo นี้เป็น **core platform** ที่ product/application repo อื่น ๆ มา consume

## ⚠️ repo นี้ไม่ implement

repo นี้มีหน้าที่ **คุมภาพรวมและเป็นเจ้าของ contract** เท่านั้น — เก็บ architecture, plane boundary, contract และ decision record

**code จริงอยู่ใน product/application repo** ที่ consume platform นี้ (ดู [Ecosystem](#ecosystem))
ถ้าจะเพิ่ม service, build tooling หรือ implementation ใด ๆ ให้ไปที่ repo ปลายทาง ไม่ใช่ที่นี่

> 🚀 **เพิ่ง repo เข้า ecosystem?** เริ่มที่ [`architecture/consumer-adoption-guide.md`](./architecture/consumer-adoption-guide.md) — คู่มือสำหรับทั้ง repo ใหม่และ repo เดิม พร้อม prompt มาตรฐานและ Definition of Done

## โฟลเดอร์ไหนเก็บอะไร

| โฟลเดอร์ | เนื้อหา | ผลผูกพัน |
| --- | --- | --- |
| [`contracts/`](./contracts) | canonical schema (YAML + JSON Schema) | ✅ ผูกพัน |
| [`profiles/`](./profiles) | ชุด config ต่อประเภทงาน — instance ของ `contracts/profile/v1` | ✅ ผูกพัน |
| [`conformance/`](./conformance) | drift check — **ข้อยกเว้นเดียวที่มี code ได้** ([ADR-0011](./decisions/0011-conformance-automation.md)) | 🔧 เครื่องมือ |
| [`decisions/`](./decisions) | ADR ระดับ ecosystem — ศัพท์และขอบเขตที่ตกลงกันแล้ว | ✅ ผูกพัน |
| [`architecture/`](./architecture) | คำอธิบาย, mapping, ผลวิเคราะห์ repo อื่น, **คู่มือนำไปใช้** | 📄 อธิบาย |
| [`planes/`](./planes) | นิยามขอบเขตของแต่ละ plane | 📄 อธิบาย |
| [`ref/`](./ref) | บันทึกดิบตามเวลา ขัดกันเองได้ | ❌ ไม่ผูกพัน |

## Planes

[`planes/`](./planes) เก็บ **นิยามขอบเขต** ของแต่ละ plane — ไม่ใช่ code

| Plane | หน้าที่ |
| --- | --- |
| [`gateway`](./planes/gateway.md) | ทางเข้า inbound — auth, policy check, quota, audit |
| [`runtime`](./planes/runtime.md) | agent loop, state, lifecycle — native + external provider |
| [`harness`](./planes/harness.md) | execution policy — บังคับลำดับขั้นภายในหนึ่งงาน |
| [`evals`](./planes/evals.md) | สนามทดสอบ — scenario, evaluator, regression |
| [`tools`](./planes/tools.md) | catalog ของ tool + MCP registration |
| [`policy`](./planes/policy.md) | ทำได้ไหม และต้องให้ใครอนุมัติ |
| [`knowledge`](./planes/knowledge.md) | ingest, retrieval, citation, ACL |
| [`workflow`](./planes/workflow.md) | orchestration ข้ามขั้น ข้าม agent |
| [`sandbox`](./planes/sandbox.md) | ที่ที่ command และ code รันจริง |
| [`observability`](./planes/observability.md) | trace, audit, cost, replay |
| [`backend-os`](./planes/backend-os.md) | data plane, connector, บ้านของ native runtime |

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

**ทะเบียนที่ผูกพันคือ [`architecture/consumers.md`](./architecture/consumers.md)** — ตารางข้างล่างเป็นภาพย่อ
ถ้าสองที่ไม่ตรงกันให้ยึดทะเบียน และแก้ที่ทะเบียนที่เดียว

| repo | บทบาท | conformance |
| --- | --- | --- |
| [`agent-platform`](https://github.com/monthop-gmail/agent-platform) | ⭐ CORE — contract · ADR · plane | — |
| [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) | Product — care agent (รันบน pstack) | ✅ `passing` |
| [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) | Product — governed DevOps | ✅ `passing` |
| [`navi-ims`](https://github.com/monthop-gmail/navi-ims) | Product — system of record (Odoo 19) | `unknown` |
| [`ai-web-harness`](https://github.com/monthop-gmail/ai-web-harness) | Harness — orchestration เหนือ gateway | `unknown` |
| [`enterprise-knowledge`](https://github.com/monthop-gmail/enterprise-knowledge) | Knowledge Plane — hybrid RAG หลัง `knowledge.search` | `unknown` |
| [`ecosystem-intelligence`](https://github.com/monthop-gmail/ecosystem-intelligence) | Engineering intelligence — **ผู้ผลิต event** | ✅ `passing` |
| [`botforge`](https://github.com/monthop-gmail/botforge) | Bot บน channel (LINE) — **ผู้ผลิต event** · manifest บน `v2` | ✅ `passing` |

**ยังไม่มี repo:** `navi-security-agent` · `agent-backend-os`
· `agent-fleet` · `model-gateway` · `farm-agent` · `odoo-farm`
— ดูว่าแต่ละตัวต้องการ contract อะไรได้ในทะเบียน

## Status

🔒 **VOCABULARY LOCKED — 2026-08-17** · ADR ทั้งหมด `Accepted` แล้ว ดู [`decisions/`](./decisions)

**ADR-0006 ownership ปิดแล้ว (2026-08-18)** — Architecture Owner ของ [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) ตอบด้วยทางที่สาม: **แยก semantics (repo ต้นทาง) ออกจาก wire schema (ที่นี่)** ดู [ADR-0006](./decisions/0006-contract-versioning.md)

**[`contracts/` v1 เขียนแล้ว](./contracts)** — `identity` `agent` `capability` `provider` `model` `tool` `mcp` `execution` `policy` `approval` `consent` `event` `artifact` `error` `profile` · ทั้งหมด validate ผ่าน JSON Schema draft 2020-12 และ cross-ref ระหว่างไฟล์ resolve ครบ

`approval/v1` และ `event/v1` เป็น **derived contract** — มีบล็อก `derived_from` ที่ pin `semantics_version` ของ [`devfactory-core/contract-semantics.yaml`](https://github.com/monthop-gmail/devfactory-core/blob/main/contract-semantics.yaml) และกำกับ 🔒 ที่ส่วนซึ่งเป็น semantics ของ repo ต้นทาง

`consent/v1` เป็น contract ที่ platform ถือ semantics เอง ([ADR-0012](./decisions/0012-consent-contract.md)) · เกณฑ์รับ contract ใหม่ 4 ข้ออยู่ที่ [`contracts/README.md`](./contracts/README.md)

**[`profiles/`](./profiles)** — `coding` `security` `knowledge` `enterprise` `workflow` `autonomous` · validate ผ่าน `contracts/profile/v1` ทั้งหมด

**[`planes/`](./planes)** — ย้ายจาก module dirs เดิมตาม [module mapping](./architecture/module-mapping.md) เรียบร้อย (`agent-harness` แยกเป็น `harness` + `evals`)

**drift check อัตโนมัติ** — ทุก PR · ทุก push เข้า `main` · และรายวันเพื่อจับกรณีที่ repo ต้นทางขยับ `semantics_version` ฝ่ายเดียว

การสื่อสารข้ามทีมใช้ GitHub: **issue** สำหรับเคาะ ADR และขอแก้ contract · **PR** สำหรับรีวิว (comment ที่บรรทัด ไม่ใช่เขียนเรียงความ) · **milestone** สำหรับดูว่าติดเฟสไหน

## Reference

- [`architecture/consumer-adoption-guide.md`](./architecture/consumer-adoption-guide.md) — **เริ่มที่นี่ถ้าจะเอา repo เข้า ecosystem** · repo ใหม่ · repo เดิม · งานข้ามหลาย repo
- [`decisions/`](./decisions) — ADR ทั้งหมดและลำดับที่ควรเคาะ
- [`contracts/`](./contracts) · [`profiles/`](./profiles) — canonical schema และ config ต่อประเภทงาน
- [`architecture/platform-architecture.md`](./architecture/platform-architecture.md) — canonical diagram (`Accepted`)
- [`architecture/consumers.md`](./architecture/consumers.md) — ทะเบียน consumer และสถานะ conformance
- [`architecture/module-mapping.md`](./architecture/module-mapping.md) — บันทึกการย้าย module เดิม → `planes/` และ `contracts/`
- [`architecture/devfactory-core-rfc-extraction.md`](./architecture/devfactory-core-rfc-extraction.md) — ดึง RFC ของ `devfactory-core` มาเป็น canonical contract อะไรได้แค่ไหน
- [`ref/`](./ref) — บันทึกดิบ พร้อมสารบัญและตารางข้อขัดแย้งที่รู้แล้ว
- [`ref/existing-repos.md`](./ref/existing-repos.md) — inventory ของ repo ที่มีอยู่จริง

## License

[MIT](./LICENSE)
