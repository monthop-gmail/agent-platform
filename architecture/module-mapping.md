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
├── modules/        เอกสารขอบเขตของแต่ละ plane
└── ref/            บันทึกดิบ ไม่ผูกพัน              ✅ มีแล้ว
```

## ตาราง mapping

| ปัจจุบัน | Action | เป้าหมาย | เหตุผล | Blocked on |
| --- | --- | --- | --- | --- |
| `backend-os/` | **move** | `modules/backend-os.md` — เอกสารขอบเขตของ repo `agent-backend-os` | เป็น implementation plane ไม่ใช่ contract; ชื่อซ้อนกับ core repo candidate | [0001](../decisions/0001-platform-scope.md), [0002](../decisions/0002-core-repository-naming.md) |
| `agent-gateway/` | **split** | `modules/gateway.md` + `contracts/gateway/` | ต้องแยกก่อนว่า gateway ตัวไหน (inbound/outbound/fan-out) | [0003](../decisions/0003-agent-gateway-boundary.md) |
| `agent-runtime/` | **split** | `modules/runtime.md` + `contracts/execution/` | state machine ระดับ task/execution เป็น contract ส่วน loop เป็นของ agent provider | [0005](../decisions/0005-agent-runtime-boundary.md) |
| `agent-harness/` | **split** | `modules/harness.md` (execution policy) + `modules/evals.md` (test rig) | คำว่า harness ถูกใช้เรียก 2 ของคนละเรื่อง | [0005](../decisions/0005-agent-runtime-boundary.md) |
| `tool-registry/` | **rename + split** | `contracts/tool/` + `contracts/mcp/` | tool schema กับ MCP transport เป็นสองเรื่อง; registry เป็น implementation | [0004](../decisions/0004-agent-vs-model-provider.md) |
| `policy-engine/` | **split** | `contracts/policy/` + `contracts/approval/` | policy outcome (allow/deny/rate-limit/budget) ≠ authority decision (APPROVE/REJECT/REQUIRE_CHANGES) — ดู [extraction §2](devfactory-core-rfc-extraction.md) | [0006](../decisions/0006-contract-versioning.md) |
| `knowledge/` | **move** | `modules/knowledge.md` — เอกสารขอบเขตของ repo `enterprise-knowledge` | knowledge เป็น product plane ไม่ใช่ contract; retrieval contract แยกไปอยู่ `contracts/tool/` (`knowledge.search`) | [0002](../decisions/0002-core-repository-naming.md), [0007](../decisions/0007-multi-tenancy.md) |
| `workflow/` | **keep + narrow** | `modules/workflow.md` + `contracts/execution/` (ส่วน orchestration) | RFC-0004 แยก orchestration/execution ไว้แล้ว | [0005](../decisions/0005-agent-runtime-boundary.md) |
| `sandbox/` | **move** | `modules/sandbox.md` | เป็น execution isolation — implementation ทั้งหมด ไม่มี contract ของตัวเองนอกจาก resource limit | [0005](../decisions/0005-agent-runtime-boundary.md) |
| `observability/` | **rename + split** | `contracts/event/` + `modules/observability.md` | event schema เป็น contract; dashboard/metrics backend เป็น implementation | [0006](../decisions/0006-contract-versioning.md), [0007](../decisions/0007-multi-tenancy.md) |

**ไม่มีแถวไหนที่เป็น `deprecated`** — ทั้ง 10 ตัวยังมีที่อยู่ เพียงย้ายชั้น

## contract ที่ต้องสร้างใหม่ (ไม่ได้มาจาก module เดิม)

| contract | ที่มา | ทำไมไม่มีใน 10 module |
| --- | --- | --- |
| `contracts/identity/` | [ADR-0007](../decisions/0007-multi-tenancy.md) · backend-os §17 | `agent_id`/`tenant_id`/`principal` กระจายอยู่ในทุก module ไม่มีเจ้าของ |
| `contracts/agent/` | contract-review P0 | นิยาม agent เอง (identity + role + instruction + capability) |
| `contracts/provider/` `contracts/model/` | [ADR-0004](../decisions/0004-agent-vs-model-provider.md) | ชั้น provider ไม่มีอยู่ในโครง 10 module เลย — ช่องว่างที่ใหญ่สุด |
| `contracts/artifact/` | contract-review P2 | file/diff/PR/report ที่ execution ผลิต |
| `contracts/error/` | decisions-first plan Phase 3 | error taxonomy ที่ทุก plane ใช้ร่วม |

## ลำดับที่ปลอดภัย

```text
1. Accept ADR-0001          → รู้ว่า repo นี้เก็บอะไรได้
2. Accept ADR-0002/0003     → ชื่อ gateway/repo นิ่ง
3. Accept ADR-0004/0005     → ศัพท์ provider/runtime นิ่ง   ← vocabulary gate
4. สร้าง contracts/ P0      → ใช้ศัพท์ที่ Accept แล้วเท่านั้น
5. ค่อย git mv 10 module    → ทำครั้งเดียว ไม่ต้องแก้ซ้ำ
```

**เหตุผลที่ยังไม่ `git mv` ตอนนี้:** 8 ใน 10 แถวขึ้นอยู่กับ ADR ที่ยังไม่เคาะ ถ้าย้ายก่อนจะต้องย้ายอีกรอบ และ link ใน `ref/` 11 ไฟล์กับ README จะเสียสองครั้ง
