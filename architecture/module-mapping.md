# Module Mapping

**Phase 5 ของ [decisions-first plan](../ref/agent-platform-decisions-first-plan.md)** — map 10 module ที่มีอยู่จริงไปยังโครงเป้าหมาย **ก่อน** จะ rename อะไร

> ⚠️ เอกสารนี้เป็น **ข้อเสนอ** ยังไม่ลงมือ — เกือบทุกแถวรอ ADR ที่ยัง `Proposed` อยู่ ห้าม rename ก่อน ADR ที่ระบุในคอลัมน์ "Blocked on" ถูก Accept

## 10 module ที่มีอยู่จริง

อ่านจาก tree จริงของ repo (ไม่ใช่จาก diagram ใน README — [`ref/agent-platform-contract-review.md`](../ref/agent-platform-contract-review.md) อ่านจาก diagram จึงเห็นแค่ 7 ตัวและชื่อไม่ตรง)

```text
backend-os/  agent-gateway/  agent-runtime/  agent-harness/  tool-registry/
policy-engine/  knowledge/  workflow/  sandbox/  observability/
```

ทั้ง 10 ตัวมีแค่ `README.md` ที่ระบุ scope — ยังไม่มี code

## โครงเป้าหมาย

ตาม [`contract-review`](../ref/agent-platform-contract-review.md) + [`decisions-first plan`](../ref/agent-platform-decisions-first-plan.md)

```text
agent-platform/
├── contracts/      canonical schema — ผูกพัน
├── decisions/      ADR ระดับ ecosystem — ผูกพัน   ✅ มีแล้ว
├── architecture/   คำอธิบาย diagram mapping        ✅ มีแล้ว
├── profiles/       ชุด config ต่อประเภทงาน
├── planes/         Plane Boundary Documentation    ← ชื่อรอ ADR-0001
└── ref/            บันทึกดิบ ไม่ผูกพัน              ✅ มีแล้ว
```

โฟลเดอร์เอกสารขอบเขต (`planes/` หรือ `modules/` — รอ [ADR-0001](../decisions/0001-platform-scope.md)) คือ **Plane Boundary Documentation**: ระบุขอบเขต ความรับผิดชอบ และสิ่งที่ห้ามทำของแต่ละ plane พร้อมชี้ว่า implementation อยู่ repo ไหน — **ไม่ใช่ที่รอ code**

## ตาราง mapping

| ปัจจุบัน | Action | เป้าหมาย | เหตุผล | Blocked on |
| --- | --- | --- | --- | --- |
| `backend-os/` | **move** | `planes/backend-os.md` — เอกสารขอบเขตของ repo `agent-backend-os` | เป็น implementation plane ไม่ใช่ contract; ชื่อซ้อนกับ core repo candidate · เป็นบ้านของ **native runtime** ตาม 0005 C2 | [0001](../decisions/0001-platform-scope.md), [0002](../decisions/0002-core-repository-naming.md) |
| `agent-gateway/` | **split** | `planes/gateway.md` + `contracts/gateway/` | ต้องแยกก่อนว่า gateway ตัวไหน (inbound/outbound/fan-out) | [0003](../decisions/0003-agent-gateway-boundary.md) |
| `agent-runtime/` | **split** | `planes/runtime.md` + `contracts/execution/` | execution contract ต้องครอบ **2 เส้นทาง** — native runtime และ external agent provider ([0005 C2](../decisions/0005-agent-runtime-boundary.md)) · loop ไม่ได้เป็นของ provider เสมอ | [0005](../decisions/0005-agent-runtime-boundary.md), [0009](../decisions/0009-capability-model.md) |
| `agent-harness/` | **split** | `planes/harness.md` (execution policy) + `planes/evals.md` (test rig) | คำว่า harness ถูกใช้เรียก 2 ของคนละเรื่อง | [0005](../decisions/0005-agent-runtime-boundary.md) |
| `tool-registry/` | **rename + split** | `contracts/tool/` + `contracts/mcp/` | tool schema กับ MCP transport เป็นสองเรื่อง; registry เป็น implementation · `risk_level` ใน tool schema ย้ายไปใช้ `action_risk` ตาม 0010 | [0004](../decisions/0004-agent-vs-model-provider.md), [0010](../decisions/0010-risk-approval-taxonomy.md) |
| `policy-engine/` | **split** | `contracts/policy/` + `contracts/approval/` | policy outcome (allow/deny/rate-limit/budget) ≠ authority decision (APPROVE/REJECT/REQUIRE_CHANGES) — ดู [extraction §2](devfactory-core-rfc-extraction.md) | [0006](../decisions/0006-contract-versioning.md), [0010](../decisions/0010-risk-approval-taxonomy.md) |
| `knowledge/` | **move** | `planes/knowledge.md` — เอกสารขอบเขตของ repo `enterprise-knowledge` | knowledge เป็น product plane ไม่ใช่ contract; retrieval contract แยกไปอยู่ `contracts/tool/` (`knowledge.search`) | [0002](../decisions/0002-core-repository-naming.md), [0007](../decisions/0007-multi-tenancy.md) |
| `workflow/` | **keep + narrow** | `planes/workflow.md` + `contracts/execution/` (ส่วน orchestration) | RFC-0004 แยก orchestration/execution ไว้แล้ว | [0005](../decisions/0005-agent-runtime-boundary.md) |
| `sandbox/` | **move** | `planes/sandbox.md` | เป็น execution isolation — implementation ทั้งหมด ไม่มี contract ของตัวเองนอกจาก resource limit · capability ระดับ host (`docker`, `network_egress`) ประกาศตาม 0009 | [0005](../decisions/0005-agent-runtime-boundary.md), [0009](../decisions/0009-capability-model.md) |
| `observability/` | **rename + split** | `contracts/event/` + `planes/observability.md` | event schema เป็น contract; dashboard/metrics backend เป็น implementation · event ต้องบันทึกทั้ง `action_risk` และ `authority` ตาม 0010 | [0006](../decisions/0006-contract-versioning.md), [0007](../decisions/0007-multi-tenancy.md), [0010](../decisions/0010-risk-approval-taxonomy.md) |

**ไม่มีแถวไหนที่เป็น `deprecated`** — ทั้ง 10 ตัวยังมีที่อยู่ เพียงย้ายชั้น

## contract ที่ต้องสร้างใหม่ (ไม่ได้มาจาก module เดิม)

| contract | ที่มา | ทำไมไม่มีใน 10 module |
| --- | --- | --- |
| `contracts/identity/` | [ADR-0007](../decisions/0007-multi-tenancy.md) · backend-os §17 | `agent_id`/`tenant_id`/`principal` กระจายอยู่ในทุก module ไม่มีเจ้าของ |
| `contracts/agent/` | contract-review P0 | นิยาม agent เอง (identity + role + instruction + capability) |
| `contracts/provider/` `contracts/model/` | [ADR-0004](../decisions/0004-agent-vs-model-provider.md) | ชั้น provider ไม่มีอยู่ในโครง 10 module เลย — ช่องว่างที่ใหญ่สุด · `provider/` มี 3 ไฟล์ (base + model + agent) |
| `contracts/capability/` | [ADR-0009](../decisions/0009-capability-model.md) | capability กระจายอยู่ 4 รูปแบบใน 3 blueprint ไม่มี module ไหนเป็นเจ้าของ |
| `contracts/artifact/` | contract-review P2 | file/diff/PR/report ที่ execution ผลิต |
| `contracts/error/` | decisions-first plan Phase 3 | error taxonomy ที่ทุก plane ใช้ร่วม |

## ลำดับที่ปลอดภัย

```text
1. Accept ADR-0001              → รู้ว่า repo นี้เก็บอะไรได้ + ชื่อโฟลเดอร์เอกสารขอบเขต
2. Accept ADR-0002/0003         → ชื่อ gateway/repo นิ่ง
3. Accept ADR-0004/0005/0009    → ศัพท์ provider/runtime/capability นิ่ง   ← vocabulary gate 🔒
4. Accept ADR-0006/0007/0010    → versioning, tenancy, risk taxonomy
5. สร้าง contracts/ P0          → ใช้ศัพท์ที่ Accept แล้วเท่านั้น
6. ค่อย git mv 10 module        → ทำครั้งเดียว ไม่ต้องแก้ซ้ำ
```

**เหตุผลที่ยังไม่ `git mv` ตอนนี้:** ทั้ง 10 แถวขึ้นอยู่กับ ADR ที่ยังไม่เคาะ (รวมชื่อโฟลเดอร์ปลายทางเองด้วย — `planes/` หรือ `modules/` ยังไม่ตัดสิน) ถ้าย้ายก่อนจะต้องย้ายอีกรอบ และ link ใน `ref/` 13 ไฟล์กับ README จะเสียสองครั้ง
