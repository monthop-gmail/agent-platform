# agent-platform

> **Agent Platform is the unified foundation for building, connecting, operating, governing, and scaling AI agents across enterprise applications.**

ชื่อนี้ไม่ผูก vendor, ไม่ผูก Cloudflare และไม่จำกัดตัวเองไว้แค่ backend — repo นี้เป็น **core platform** ที่ product/application repo อื่น ๆ มา consume

## ⚠️ repo นี้ไม่ implement

repo นี้มีหน้าที่ **คุมภาพรวมและเป็นเจ้าของ contract** เท่านั้น — เก็บ architecture, plane boundary, contract และ decision record

**code จริงอยู่ใน product/application repo** ที่ consume platform นี้ (ดู [Ecosystem](#ecosystem))
ถ้าจะเพิ่ม service, build tooling หรือ implementation ใด ๆ ให้ไปที่ repo ปลายทาง ไม่ใช่ที่นี่

## โฟลเดอร์ไหนเก็บอะไร

| โฟลเดอร์ | เนื้อหา | ผลผูกพัน |
| --- | --- | --- |
| [`contracts/`](./contracts) | canonical schema (YAML + JSON Schema) | ✅ ผูกพัน |
| [`profiles/`](./profiles) | ชุด config ต่อประเภทงาน — instance ของ `contracts/profile/v1` | ✅ ผูกพัน |
| [`decisions/`](./decisions) | ADR ระดับ ecosystem — ศัพท์และขอบเขตที่ตกลงกันแล้ว | ✅ ผูกพัน |
| [`architecture/`](./architecture) | คำอธิบาย, mapping, ผลวิเคราะห์ repo อื่น | 📄 อธิบาย |
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

**[`contracts/` v1 เขียนแล้ว](./contracts)** — `identity` `agent` `capability` `provider` `model` `tool` `mcp` `execution` `policy` `artifact` `error` `profile` · ทั้งหมด validate ผ่าน JSON Schema draft 2020-12 และ cross-ref ระหว่างไฟล์ resolve ครบ

`approval/` และ `event/` **ยังไม่เขียน** — ติดสถานะ `external-authority-pending` เพราะมาจาก RFC ของ `devfactory-core` ที่ authority ยังไม่ย้าย

**[`profiles/`](./profiles)** — `coding` `security` `knowledge` `enterprise` `workflow` `autonomous` · validate ผ่าน `contracts/profile/v1` ทั้งหมด

**[`planes/`](./planes)** — ย้ายจาก module dirs เดิมตาม [module mapping](./architecture/module-mapping.md) เรียบร้อย (`agent-harness` แยกเป็น `harness` + `evals`)

การสื่อสารข้ามทีมใช้ GitHub: **issue** สำหรับเคาะ ADR และขอแก้ contract · **PR** สำหรับรีวิว (comment ที่บรรทัด ไม่ใช่เขียนเรียงความ) · **milestone** สำหรับดูว่าติดเฟสไหน

## Reference

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
