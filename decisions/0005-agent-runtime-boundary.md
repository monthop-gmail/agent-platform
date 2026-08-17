# ADR-0005: Agent Runtime Boundary

**Status:** Proposed
**Date:** 2026-08-17
**Depends on:** ADR-0003, ADR-0004
**Blocking:** `contracts/execution/`, module `agent-runtime/` `agent-harness/` `workflow/` `sandbox/` — **vocabulary gate**

## Context

มี 5 คำที่หน้าที่คาบเกี่ยวกันและไม่มีเอกสารไหนแบ่งให้ชัด: **runtime · harness · workflow · orchestration · sandbox**

ที่ขัดกันตรง ๆ:

| เอกสาร | จุดยืนเรื่อง runtime |
| --- | --- |
| [`backend-os §6`](../ref/enterprise-agent-backend-os-blueprint.md) | **สร้าง runtime เอง** — Durable Objects เป็น stateful agent runtime |
| [`knowledge-platform §5`](../ref/enterprise-agent-knowledge-platform-blueprint.md) | **ไม่สร้างเอง** — "Platform ไม่สร้าง Agent Runtime เองทั้งหมด" ใช้ adapter ต่อกับ Claude Code / Hermes / OpenCode |

และคำว่า harness ก็ใช้คนละความหมาย:

| ที่มา | harness หมายถึง |
| --- | --- |
| [`ai-web-harness`](https://github.com/monthop-gmail/ai-web-harness) (ของจริง) | บังคับ workflow การสร้างเว็บ (requirement→design→implement→test→review→fix) + `harness/checks` |
| [`knowledge-platform §8`](../ref/enterprise-agent-knowledge-platform-blueprint.md) | execution policy บังคับลำดับ intent→permission→retrieval→reasoning→tool→verify |
| [`navi-security-agent §6`](../ref/navi-security-agent-blueprint.md) | สนามทดสอบ — `harness/scenarios/*.yaml` + evaluators + reports |
| [`ai-subscription-oauth-gateway §17`](../ref/ai-subscription-oauth-gateway-blueprint.md) | ชั้น orchestration ที่อยู่**เหนือ** gateway ("Harness = ทำงานอย่างไร") |

→ harness ถูกใช้เรียกทั้ง **execution policy** และ **test/eval rig** ซึ่งเป็นของคนละเรื่อง

`devfactory-core` RFC-0004 ให้เส้นแบ่งที่ใช้ได้: **Orchestration** (decompose, dependency, retry, schedule) vs **Execution** (perform, report, sandbox) + ห้าม execution ตัดสิน governance และห้าม orchestration แก้ artifact เอง

## Options

### A. 4 ชั้น + แยก harness เป็น 2 คำ (แนะนำ)

```text
Workflow / Orchestration   งานหลายขั้น หลาย agent — decompose, dependency, retry, schedule, human step
        ↓
Harness (execution policy)  บังคับลำดับขั้นภายในหนึ่งงาน — intent → permission → retrieve → reason → tool → verify
        ↓
Runtime                     agent loop เดียว — session, state, context assembly, tool call, lifecycle
        ↓
Sandbox                     ที่ที่ command/code รันจริง — isolation, resource limit, egress policy
```

และแยกคำ:

| คำ | ความหมายที่ lock |
| --- | --- |
| **Harness** | execution policy — บังคับว่าขั้นตอนต้องเดินตามลำดับไหน |
| **Evals / Scenarios** | test rig — สิ่งที่ `navi-security-agent §6` เรียกว่า harness ให้เปลี่ยนไปใช้คำนี้ |

* ✅ ตรงกับ RFC-0004 (workflow=orchestration, runtime+sandbox=execution)
* ✅ อธิบาย `ai-web-harness` ได้ถูก — มันเป็น harness ชั้นบน ไม่ใช่ runtime
* ✅ ทำให้ module `agent-harness/` กับ `workflow/` กับ `sandbox/` มีเส้นแบ่ง
* ❌ `navi-security-agent` ต้องเปลี่ยนชื่อโฟลเดอร์ `harness/` → `evals/` (หรือคงชื่อไว้แต่รู้ว่าคือ evals)

### B. รวม harness เข้า runtime

* ✅ น้อยชั้น
* ❌ `ai-web-harness` มีอยู่จริงเป็น repo แยกแล้ว และ §17 ระบุชัดว่าอยู่เหนือ gateway → ขัดของจริง

### C. รวม workflow เข้า harness

* ❌ workflow ต้อง durable/resumable ข้าม process ส่วน harness เป็น policy ภายใน request — คนละ lifetime

## Options — platform สร้าง runtime เองหรือไม่

### A2. ไม่สร้าง — platform เป็นเจ้าของ contract, runtime มาจาก agent provider (แนะนำ ถ้า ADR-0001 = A)

* ✅ สอดคล้อง ADR-0001 (repo นี้ไม่ implement) และ knowledge-platform §5
* ✅ ใช้ของที่มีอยู่จริง (Claude Code, Codex, OpenCode) ได้ทันทีตาม ADR-0004
* ⚠️ ต้องยอมรับว่า runtime ภายนอกไม่ได้ implement contract ครบ → ต้องมี capability declaration (`supports(...)` ตาม `ai-subscription-oauth-gateway §7`)

### B2. สร้าง runtime กลางเอง (Durable Objects ตาม backend-os §6)

* ✅ ควบคุม state/resume/budget ได้เต็มที่
* ❌ ผูก Cloudflare (ขัดหลัก "ไม่ผูก vendor" ที่ทั้ง 4 blueprint ย้ำ) — เว้นว่าจะทำเป็น provider หนึ่งใน `agent-backend-os`
* ❌ ขัด ADR-0001 ถ้าจะสร้างใน repo นี้

## Decision

> _(รอเคาะ — ต้องตอบ 2 ส่วน: 4 ชั้น และ platform สร้าง runtime เองหรือไม่)_

## Consequences ถ้าเลือก A + A2

* module `agent-runtime/` ใน repo นี้ = เอกสาร contract ของ runtime ไม่ใช่ที่รอ code
* module `agent-harness/` = execution policy · เพิ่ม `evals/` แยกออกมา หรือระบุใน module mapping (ADR ไม่ตัดสินให้)
* `contracts/execution/` ต้องมี state machine ระดับ task/execution เอง เพราะ RFC-0001 ครอบแค่ระดับ job และเขียนไว้เองว่า task-level ยังเป็น Future Work — ดู [extraction §4](../architecture/devfactory-core-rfc-extraction.md)
* ต้องตอบ open question ที่ RFC-0001 ทิ้งไว้: **retry semantics ของ FAILED** และ **parallel task substates**

## Sources

`devfactory-core/rfcs/0004` · [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §1, §4 · [`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §6 · [`../ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §5, §8 · [`../ref/navi-security-agent-blueprint.md`](../ref/navi-security-agent-blueprint.md) §6 · [`../ref/existing-repos.md`](../ref/existing-repos.md)
