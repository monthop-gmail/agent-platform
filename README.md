# agent-platform

> **Agent Platform is the unified foundation for building, connecting, operating, governing, and scaling AI agents across enterprise applications.**

ชื่อนี้ไม่ผูก vendor, ไม่ผูก Cloudflare และไม่จำกัดตัวเองไว้แค่ backend — repo นี้เป็น **core platform** ที่ product/application repo อื่น ๆ มา consume

## ⚠️ repo นี้ไม่ implement

repo นี้มีหน้าที่ **คุมภาพรวมและปรับปรุงโครง module** เท่านั้น — เก็บ architecture, module boundary, contract และ decision record

**code จริงอยู่ใน product/application repo** ที่ consume platform นี้ (ดู [Ecosystem](#ecosystem))
ถ้าจะเพิ่ม service, build tooling หรือ implementation ใด ๆ ให้ไปที่ repo ปลายทาง ไม่ใช่ที่นี่

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

โครง module รอบแรกวางแล้ว — ยังอยู่ในขั้นตอนปรับปรุงขอบเขตและ boundary ระหว่าง module

## Reference

- [`ref/repo-naming-agent-platform.md`](./ref/repo-naming-agent-platform.md) — เหตุผลและตัวเลือกอื่นที่พิจารณาก่อนเลือกชื่อ `agent-platform`

## License

[MIT](./LICENSE)
