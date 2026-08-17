# ADR-0005: Agent Runtime Boundary

**Status:** Accepted (2026-08-17)
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

## แยก Agent Execution ออกเป็นส่วนย่อยก่อน

คำว่า "runtime" ถูกใช้เรียกก้อนเดียวที่จริง ๆ มี 5 ส่วนแยกกันได้:

```text
Agent
  │
  ▼
Agent Execution
  ├── orchestration loop     ใครตัดสินว่ารอบถัดไปทำอะไร
  ├── provider execution     ใครเรียก model / agent provider จริง
  ├── tool calls             ใครแปลง tool call เป็น action
  ├── state                  session, memory, context ถูกเก็บที่ไหน
  └── lifecycle              spawn / resume / cancel / timeout
```

ประโยชน์คือแต่ละส่วนตอบได้ว่า **platform เป็นเจ้าของหรือ provider เป็นเจ้าของ** โดยไม่ต้องเลือกทั้งก้อน:

| ส่วน | Claude Code / OpenCode (external) | agent ที่เราเขียนเอง |
| --- | --- | --- |
| orchestration loop | provider ทำเอง (มองไม่เห็นข้างใน) | platform runtime ทำ |
| provider execution | provider ทำเอง | platform เรียก model provider |
| tool calls | provider ทำเอง + platform ตรวจผ่าน gateway | platform ทำ |
| state | provider ถือ session ของตัวเอง | platform ถือ |
| lifecycle | platform สั่งผ่าน adapter (`cancel()`) | platform ถือ |

## Options — platform สร้าง runtime เองหรือไม่

### C2. Platform Runtime = native runtime + external agent provider ใต้ contract เดียว (แนะนำ)

```text
contracts/execution/   ← execution contract เดียว ทั้งสองทางต้องทำตาม
        │
   ┌────┴─────────────────────┐
   ▼                          ▼
native runtime          external agent provider
(agent-backend-os)      (Claude Code / OpenCode / Hermes / Codex)
```

* ✅ **agent ที่ทีมเขียนเองไม่เป็น citizen ชั้นสอง** — ไม่ต้องห่อตัวเองเป็น "provider ปลอม" เพื่อจะรันได้
* ✅ ครอบกรณีที่ agent ไม่มี loop ของตัวเอง (agent ที่เป็นแค่ prompt + tool set) — native runtime ให้ loop
* ✅ ไม่ขัด ADR-0001 เพราะ **native runtime ไม่ได้อยู่ใน repo นี้** — อยู่ใน `agent-backend-os` ส่วน repo นี้ถือแค่ contract
* ✅ ไม่ผูก vendor — Cloudflare/DO เป็นทางเลือก implementation ของ native runtime ตัวหนึ่ง ไม่ใช่ข้อบังคับ
* ⚠️ contract ต้องออกแบบให้ทั้งสองฝั่งเติมได้ไม่เท่ากัน → ต้องพึ่ง capability declaration ([ADR-0009](0009-capability-model.md)) ระบุว่าเส้นทางไหนรองรับอะไร
* ⚠️ execution ที่ผ่าน external provider จะ observe ได้หยาบกว่า (มองไม่เห็น step ข้างใน) → `contracts/event/` ต้องยอมรับ trace ที่ไม่มี step ย่อย

### A2. ไม่สร้างเลย — runtime มาจาก agent provider เท่านั้น

* ✅ สอดคล้อง ADR-0001 ตรงตัวที่สุด และตรงกับ knowledge-platform §5
* ✅ ใช้ของที่มีอยู่จริงได้ทันที ไม่ต้องเขียน runtime
* ❌ **agent ที่ทีมเขียนเองไม่มีที่ยืน** — ต้องแพ็กตัวเองเป็น agent provider ทั้งที่เป็น agent ธรรมดา
* ❌ agent ง่าย ๆ (prompt + tool 2 ตัว) ต้องมี process/CLI ของตัวเองเพื่อจะเป็น provider → ต้นทุนไม่สมเหตุสมผล

### B2. สร้าง native runtime เท่านั้น (Durable Objects ตาม backend-os §6)

* ✅ ควบคุม state/resume/budget/trace ได้เต็มที่และสม่ำเสมอ
* ❌ ทิ้งของที่มีอยู่จริง (Claude Code, Codex, OpenCode) ซึ่งเป็นเหตุผลตั้งต้นของ `ai-subscription-oauth-gateway` และ `distributed-gateway`
* ❌ ถ้า implement ใน repo นี้ = ขัด ADR-0001

## Decision

**A + C2**

* **A** — 4 ชั้น `Workflow → Harness → Runtime → Sandbox` และแยกคำ **Harness** (execution policy) ออกจาก **Evals** (test rig)
* **C2** — Platform Runtime = **native runtime + external agent provider ใต้ execution contract เดียวกัน**

**Reason:** 4 ชั้นตรงกับเส้นแบ่ง orchestration/execution ของ `devfactory-core` RFC-0004 และอธิบาย `ai-web-harness` ที่มีอยู่จริงได้ถูกว่าเป็น harness ไม่ใช่ runtime · เลือก C2 แทน A2 เพราะไม่ใช่ทุก agent มี loop ของตัวเอง — agent ที่เป็นแค่ prompt + tool set ไม่ควรต้องแพ็กตัวเองเป็น agent provider เพื่อให้รันได้ ซึ่งจะทำให้ agent ที่ทีมเขียนเองกลายเป็น citizen ชั้นสอง · C2 ไม่ขัด ADR-0001 เพราะ native runtime อยู่ที่ `agent-backend-os` ไม่ใช่ repo นี้ · ปฏิเสธ B2 เพราะทิ้ง Claude Code / Codex / OpenCode ที่มีอยู่จริง

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

native runtime ลงทะเบียนเป็น agent provider ตัวหนึ่งตาม ADR-0004 — ไม่มี provider ที่เป็น "ของเรา" แบบมีสิทธิ์พิเศษ

## Consequences ถ้าเลือก A + C2

* module `agent-runtime/` ใน repo นี้ = เอกสารขอบเขต + `contracts/execution/` ไม่ใช่ที่รอ code · native runtime ไปอยู่ `agent-backend-os`
* module `agent-harness/` = execution policy · เพิ่ม `evals/` แยกออกมา หรือระบุใน module mapping (ADR ไม่ตัดสินให้)
* `contracts/execution/` ต้องมี **execution mode** ระบุว่างานนี้เดินทางไหน:

```yaml
execution_mode: native | provider        # ใครถือ orchestration loop
provider: claude-code | null             # null = native runtime
observability_depth: step | turn         # provider มักได้แค่ turn
```

* `contracts/execution/` ต้องมี state machine ระดับ task/execution เอง เพราะ RFC-0001 ครอบแค่ระดับ job และเขียนไว้เองว่า task-level ยังเป็น Future Work — ดู [extraction §4](../architecture/devfactory-core-rfc-extraction.md)
* ต้องตอบ open question ที่ RFC-0001 ทิ้งไว้: **retry semantics ของ FAILED** และ **parallel task substates**
* กฎที่ต้องคงไว้ทั้งสองเส้นทาง (จาก RFC-0004): execution ไม่ตัดสิน governance · ไม่แตะ backend resource ตรง · ไม่ถือ provider credential เอง — external provider ก็ต้องผ่าน gateway เหมือนกัน ไม่มีสิทธิ์พิเศษเพราะเป็นของ vendor

## Sources

`devfactory-core/rfcs/0004` · [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §1, §4 · [`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §6 · [`../ref/enterprise-agent-knowledge-platform-blueprint.md`](../ref/enterprise-agent-knowledge-platform-blueprint.md) §5, §8 · [`../ref/navi-security-agent-blueprint.md`](../ref/navi-security-agent-blueprint.md) §6 · [`../ref/existing-repos.md`](../ref/existing-repos.md)
