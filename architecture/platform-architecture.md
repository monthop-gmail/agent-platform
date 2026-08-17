# Platform Architecture

**Status: Accepted (2026-08-17)** — canonical architecture ของ platform

ทุกชั้นในนี้อ้างอิง ADR ที่ Accepted แล้ว ([vocabulary gate ผ่านครบ](../decisions/)) · เปลี่ยน diagram นี้ได้ต่อเมื่อมี ADR ใหม่ที่ supersede ADR ที่เกี่ยวข้อง

## Canonical diagram

```text
                       AGENT PLATFORM
                              │
                    ┌─────────┴─────────┐
                    │ PLATFORM CONTRACT │
                    └─────────┬─────────┘
                              │
        ┌─────────────┬───────┼────────┬────────────┐
        ▼             ▼       ▼        ▼            ▼
     Identity      Gateway  Runtime  Workflow     Policy
        │             │       │        │            │
        └─────────────┴───────┼────────┴────────────┘
                              │
                   Capability Routing  (ADR-0009)
                              │
              ┌───────────────┴──────────────┐
              ▼                              ▼
       Model Providers                 Agent Providers   (ADR-0004)
              │                              │
      OpenAI / Claude                 Claude Code
      Gemini / Qwen                   Gemini CLI
      DeepSeek / ...                  Codex / OpenCode
              │                              │
              └──────────────┬───────────────┘
                             ▼
                     Tools / MCP / Sandbox
                             │
                             ▼
                    Enterprise Systems
                (Odoo · IoT/VMS · GitHub · DB)
```

## อ่าน diagram นี้อย่างไร

### ทุกอย่างแขวนใต้ Platform Contract

contract เป็นชั้นบนสุด **ไม่ใช่เพราะมันทำงาน** แต่เพราะทุกชั้นล่างต้องพูดภาษาเดียวกัน — repo นี้เป็นเจ้าของแค่กล่องนั้นกล่องเดียว ที่เหลือเป็น implementation ใน repo ลูก ([ADR-0001](../decisions/0001-platform-scope.md))

### 5 plane ที่อยู่ระดับเดียวกัน

`Identity` · `Gateway` · `Runtime` · `Workflow` · `Policy` วางแนวนอนเพราะไม่มีใครอยู่ใต้ใคร — แต่ละตัวถูกเรียกได้จากทุกตัว ต่างจาก diagram รุ่นแรกที่วาง Gateway → Runtime → Backend เป็นลำดับ ซึ่งซ่อนความจริงว่า Policy ถูกเรียกทั้งตอน gateway และตอน runtime

### Capability Routing เป็นชั้นแยก ไม่ใช่ field

จุดที่ต่างจาก diagram เดิมที่สุด — การเลือกว่าใครทำงานนี้ **ไม่ได้ถามว่า "ใช้ provider ไหน"** แต่ถามว่า "ใครทำสิ่งนี้ได้"

```text
task requirement          →  capability routing  →  ที่เลือกได้
──────────────────────       ──────────────────     ──────────────
github + code_execution      + tenant/policy        native runtime
+ filesystem                 + cost / quota         Claude Code
                             + availability         OpenCode
                                                    Codex CLI
```

ถ้า capability เป็นแค่ field ของ provider จะตอบคำถามย้อนทางนี้ไม่ได้ ([ADR-0009](../decisions/0009-capability-model.md))

### Model Providers ≠ Agent Providers

สองกล่องนี้อยู่ระดับเดียวกันแต่ **shape ต่างกัน** — model provider ให้ inference, agent provider ให้ execution (มี loop/tool/workspace ของตัวเอง) `Claude` ปรากฏสองฝั่งเพราะเป็นสองสิ่ง ([ADR-0004](../decisions/0004-agent-vs-model-provider.md))

และ native runtime ที่เราเขียนเองก็ลงทะเบียนเป็น agent provider ตัวหนึ่ง ไม่มีสิทธิ์พิเศษ ([ADR-0005 C2](../decisions/0005-agent-runtime-boundary.md))

### Tools / MCP / Sandbox เป็นทางเดียวที่แตะระบบจริง

ทั้งสองเส้นทาง (native / external provider) ต้องผ่านชั้นนี้ — **ห้าม provider เรียก Enterprise Systems ตรง** ไม่ว่าจะเป็นของ vendor หรือของเราเอง

หลักนี้มาจาก 3 แหล่งที่เห็นตรงกัน:

| แหล่ง | ถ้อยคำ |
| --- | --- |
| `devfactory-core` RFC-0004 | Execution making governance decisions → forbidden |
| [`navi-security-agent §3`](../ref/navi-security-agent-blueprint.md) | AI ≠ Authority |
| [`backend-os §4`](../ref/enterprise-agent-backend-os-blueprint.md) | ห้ามให้ Agent เข้าถึง backend resource โดยตรง |

## สิ่งที่ diagram นี้ยังไม่แสดง

จงใจตัดออกเพื่อให้อ่านได้ — อยู่ในเอกสารอื่น:

| ไม่มีใน diagram | อยู่ที่ |
| --- | --- |
| Event bus / audit trail ที่ไหลขึ้นจากทุกชั้น | [ADR-0006](../decisions/0006-contract-versioning.md) · [extraction §3](devfactory-core-rfc-extraction.md) |
| Human approval loop | [ADR-0010](../decisions/0010-risk-approval-taxonomy.md) |
| Knowledge / Memory | [`ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) |
| Tenant/workspace ที่ครอบทุกกล่อง | [ADR-0007](../decisions/0007-multi-tenancy.md) |
| ทิศทาง traffic ของ gateway 3 แบบ | [ADR-0003](../decisions/0003-agent-gateway-boundary.md) |

## เทียบกับ diagram ใน README

README ใช้เวอร์ชันย่อ (Gateway / Runtime / Knowledge → Enterprise Backend) ซึ่ง**ยังถูกในระดับ ecosystem** แต่ไม่แสดง capability routing และไม่แยก provider สองชั้น

* README = ภาพให้คนนอกเข้าใจใน 10 วินาที
* ไฟล์นี้ = ภาพสำหรับคนที่จะเขียน contract หรือ implement plane

## ที่มา

diagram ต้นฉบับจาก [`ref/agent-platform-adr-review-2.md`](../ref/agent-platform-adr-review-2.md) · เพิ่มหมายเหตุว่าชั้นไหนอ้างอิง ADR ตัวไหน และปรับเป็น `Accepted` เมื่อ ADR-0004/0005/0009 ถูกเคาะเมื่อ 2026-08-17
