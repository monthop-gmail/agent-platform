# devfactory-core RFC Extraction

**Phase 1 ของ [decisions-first plan](../ref/agent-platform-decisions-first-plan.md)** — ดึงของที่มีอยู่แล้วใน `devfactory-core` มาเป็นฐานของ canonical contract แทนการออกแบบซ้ำ

อ่านจาก [`monthop-gmail/devfactory-core`](https://github.com/monthop-gmail/devfactory-core) `main` เมื่อ 2026-08-17

## สรุปสถานะต้นทาง

RFC ทั้ง 4 ตัวเป็น **Status: Draft** และสั้นมาก (765–1,347 bytes) — เป็น *skeleton ที่ semantics ถูก* ไม่ใช่ schema ที่ใช้ได้ทันที

| RFC | สิ่งที่ให้ | สถานะ |
| --- | --- | --- |
| 0001 Job State Machine | 10 states + transition rules | Draft |
| 0002 Governance Decision Contract | 3 decision types + 4 required fields | Draft |
| 0003 Audit & Event Log Schema | 7 event types + 5 required fields | Draft |
| 0004 Orchestration vs Execution Boundary | responsibility split + forbidden list | Draft |

---

## 1. ยกมาเป็น canonical ได้เลย — RFC-0004 (boundary)

เป็นตัวที่แข็งที่สุดและ **ตรงกับอีก 3 blueprint ของเราโดยไม่ต้องแก้**

```text
Orchestration : task decomposition · dependency · retry · scheduling
Execution     : perform task · report result · operate in sandbox

Forbidden:
  - Execution making governance decisions
  - Orchestration modifying artifacts directly
```

หลัก "execution ตัดสิน governance เองไม่ได้" ปรากฏใน 3 ที่ด้วยถ้อยคำต่างกัน:

| เอกสาร | ถ้อยคำ |
| --- | --- |
| `devfactory-core` RFC-0004 | Execution making governance decisions → forbidden |
| `ref/navi-security-agent-blueprint.md` §3 | **AI ≠ Authority** |
| `ref/enterprise-agent-backend-os-blueprint.md` §4 | ห้ามให้ Agent เข้าถึง backend resource โดยตรง |

→ **3 แหล่งเห็นตรงกัน = principle ที่ lock ได้** ใช้เป็นฐานของ [ADR-0005](../decisions/0005-agent-runtime-boundary.md)

---

## 2. ต้องแยกเป็น 2 contract ไม่ใช่อันเดียว — RFC-0002

RFC-0002 ให้:

```text
Decision Types:   APPROVE · REJECT · REQUIRE_CHANGES
Required Fields:  decision · reason · timestamp · authority
Guarantees:       immutable · every APPROVE auditable · no execution without APPROVE
```

แต่ `ref/enterprise-agent-backend-os-blueprint.md` §8 ต้องการ outcome 5 แบบ:

```text
allow · deny · approval · rate-limit · budget-limit
```

**สองอันนี้ไม่ใช่ของเดียวกัน** — RFC-0002 คือ *คำตัดสินของผู้มีอำนาจ (มนุษย์/authority)* ส่วน §8 คือ *ผลการประเมินของ policy engine* การยัดรวมกันจะทำให้ `rate-limit` กลายเป็น "decision" ที่ต้องมี `authority` ซึ่งไม่มีความหมาย

→ แยกเป็น:

```text
contracts/approval/   ← RFC-0002 (APPROVE / REJECT / REQUIRE_CHANGES + authority)
contracts/policy/     ← backend-os §8 (allow / deny / escalate + rate/budget limit)
```

โดย policy ที่ผลออกมาเป็น `approval` จึงจะไปสร้าง approval request ตาม contract ตัวแรก

### field ที่ต้องเพิ่มสำหรับใช้ระดับ platform

RFC-0002 มี 4 fields ซึ่งพอสำหรับ devfactory (job-centric) แต่ขาด:

```text
tenant_id · execution_id · agent_id · risk_level · policy_id
expires_at (approval มีอายุ) · escalation_target
```

---

## 3. ต้องขยาย field แต่เก็บ semantics — RFC-0003

RFC-0003 ให้ 7 event types + 5 required fields:

```text
JOB_CREATED · STATE_TRANSITION · GOVERNANCE_DECISION · TASK_ASSIGNED
EXECUTION_STARTED · EXECUTION_FAILED · JOB_COMPLETED

event_id · job_id · event_type · timestamp · source
```

Guarantees ที่ใช้ได้เลย: **append-only** · **no silent state change**

### ปัญหา 2 ข้อเมื่อเอามาใช้ทั้ง ecosystem

**(ก) `job_id` เป็น required แต่ไม่ใช่ทุก event มี job** — agent run ที่เป็น chat turn, retrieval, หรือ observer event จาก `navi-ims` ไม่ได้เกิดจาก job → ต้องเปลี่ยนเป็น `subject_id` + `subject_type` หรือทำ `job_id` เป็น optional พร้อม `correlation_id` (RFC-0003 เขียนไว้ใน Future Work ว่า "Correlation IDs" อยู่แล้ว)

**(ข) field น้อยกว่าที่ blueprint ต้องการ** — `ref/enterprise-agent-backend-os-blueprint.md` §14 ระบุ 13 fields:

```text
tenant_id · agent_id · user_id · session_id · tool_id · resource · action
policy_result · approval · execution_time · cost · result · error
```

RFC-0003 Future Work เขียนไว้ว่า "Cost attribution" → ตรงกัน ไม่ขัดกัน แค่ยังไม่ทำ

→ **เอา 7 event types + append-only guarantee เป็น canonical, ขยาย field set ตาม §14, ทำ `job_id` เป็น optional**

หมายเหตุ: §14 มีข้อกำกับสำคัญที่ RFC-0003 ไม่มี — **ไม่เก็บ chain-of-thought ที่เป็น private reasoning** เก็บเป็น structured metadata แทน ควรยกมาใส่ contract ด้วย

---

## 4. แบ่งชั้นกับ RFC-0001 — job ≠ task ≠ execution

RFC-0001 มี 10 states ระดับ **job**:

```text
DRAFT → GOVERNANCE_ANALYSIS → APPROVED / REJECTED →
TASK_PLANNING → IN_PROGRESS → VALIDATING → DEPLOYABLE → COMPLETED / FAILED
```

ส่วน `ref/distributed-multi-agent-gateway-blueprint.md` Phase 1 ต้องการ state machine ระดับ **task** (`POST /tasks` → `task_id` → poll → timeout/retry/cancel) ซึ่งละเอียดกว่าและอายุสั้นกว่า

RFC-0001 Future Work เขียนไว้เองว่า **"Task-level state machine"** ยังไม่ทำ → ช่องนี้ว่างอยู่พอดี

→ เสนอแบ่งความเป็นเจ้าของ:

| ระดับ | เจ้าของ | ตัวอย่าง |
| --- | --- | --- |
| **Job** (งานที่ผ่าน governance) | `devfactory-core` RFC-0001 | "แก้ issue #123" |
| **Task / Execution** (หน่วยที่ส่งให้ worker) | `agent-platform/contracts/execution/` | "รัน claude-code ใน worker-01" |
| **Step** (tool call / model call) | `agent-platform/contracts/event/` | "เรียก github.pr.create" |

RFC-0001 Open Questions ที่ยังไม่ตอบและ platform ต้องตอบด้วย: **retry semantics for FAILED** และ **parallel task substates**

---

## 5. ของแถมที่ควรก๊อปมาทั้งแพตเทิร์น

### `docs/governance/CORE_BOUNDARY.md`

devfactory-core ทำสิ่งเดียวกับที่ `agent-platform` ต้องทำ — ประกาศว่า v0.x ทำอะไรได้/ไม่ได้ ในรูป checklist สั้น ๆ:

```text
✅ เพิ่ม RFC และเอกสารสเปก / skeleton / interface-contract (ไม่ผูก tech) / diagram / test logic
❌ เปลี่ยน lifecycle โดยไม่มี RFC / framework ที่ผูก vendor / UI / chatbot / auto-deploy ที่ไม่ผ่าน governance
```

บรรทัด **"เพิ่ม interface / contract (ไม่ผูก tech)"** คือคำตอบของ [ADR-0008](../decisions/0008-reference-stack.md) อยู่แล้ว

### `GOVERNANCE.md`

```text
- RFC required for architectural change
- Majority maintainer approval required
- Architecture Owner has final decision authority
```

→ ใช้เป็นฐานของ [ADR-0006 contract versioning](../decisions/0006-contract-versioning.md) ได้ตรง ๆ

### `README.md` Direction Lock + Architectural Principles

6 หลักการที่ประกาศไว้ ใช้ได้กับ platform ทั้งหมด:

```text
1. Governance before execution
2. Explicit state machine workflow
3. Separation of control and execution planes
4. Immutable audit trail
5. Cost isolation per provider
6. No agent has total authority
```

---

## 6. เรื่องชื่อที่ต้องระวัง

`devfactory-core` เก็บ architectural decision ไว้ที่ **`rfcs/`** แต่ `agent-platform` ตามแผนใช้ **`decisions/`** — สองที่นี้จะมีของคล้ายกันคนละชื่อ

เสนอ: `decisions/` = ADR ระดับ ecosystem (ผูกหลายrepo) · `rfcs/` ใน repo ลูก = spec ภายใน repo นั้น และให้ ADR อ้าง RFC ได้ แต่ห้าม RFC ใน repo ลูกแก้ contract กลางเอง

---

## สรุปว่าเอาอะไรมาใช้ได้แค่ไหน

| ของ | เอามาใช้ | ต้องทำเพิ่ม |
| --- | --- | --- |
| RFC-0004 boundary | ✅ ทั้งหมด | — |
| RFC-0003 event types + append-only | ✅ semantics | ขยาย 13 fields, `job_id` optional, ห้ามเก็บ CoT |
| RFC-0002 approval | ✅ 3 decision types | เพิ่ม 7 fields, แยก `policy/` ออกจาก `approval/` |
| RFC-0001 job states | ✅ ระดับ job | platform ต้องเขียน task/execution state เอง |
| CORE_BOUNDARY / GOVERNANCE pattern | ✅ ก๊อปโครง | เขียนเวอร์ชันของ platform |

**ไม่มีอะไรขัดกันจริงจัง** — ที่ดูเหมือนขัดคือ RFC-0002 vs policy outcome ซึ่งแก้ได้ด้วยการแยกเป็น 2 contract และ RFC-0001 vs task state ซึ่งแก้ได้ด้วยการแบ่งชั้น

⚠️ ทั้ง 4 RFC เป็น **Draft** — ถ้า `agent-platform` จะถือเป็น canonical ต้องตกลงกับ Architecture Owner ของ `devfactory-core` ก่อนว่าใครมีอำนาจแก้ ([ADR-0006](../decisions/0006-contract-versioning.md))
