# Decisions (ADR)

ที่เก็บข้อตัดสินใจระดับ **ecosystem** — เรื่องที่ผูกหลาย repo และเปลี่ยนภายหลังแพง

ADR ในโฟลเดอร์นี้เป็น **authority** ของศัพท์และขอบเขต ถ้าเอกสารใน [`../ref/`](../ref/) ขัดกับ ADR ที่ Accepted แล้ว → ADR ชนะ (ref เป็นบันทึกดิบตามเวลา ไม่ใช่ข้อตกลง)

## กติกา

* หนึ่งไฟล์ = หนึ่งข้อตัดสินใจ ตั้งเลขเรียงไม่ซ้ำ ไม่ลบไฟล์เก่า
* Status: `Proposed` → `Accepted` / `Rejected` → `Superseded by NNNN`
* แก้ ADR ที่ Accepted แล้วไม่ได้ — ต้องเขียนตัวใหม่ที่ supersede
* ADR ต้องมี **Options ที่พิจารณา** ไม่ใช่แค่คำตอบ เพื่อให้คนมาใหม่รู้ว่าทำไมไม่เลือกทางอื่น
* repo ลูกเก็บ spec ภายในที่ `rfcs/` ของตัวเอง (เช่น `devfactory-core/rfcs/`) และ **ห้ามแก้ contract กลางเอง**

## สถานะปัจจุบัน — 🔒 VOCABULARY LOCKED (2026-08-17)

**Authority ของทั้งชุด:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

| ADR | เรื่อง | Decision | Status |
| --- | --- | --- | --- |
| [0001](0001-platform-scope.md) | Platform scope | **A + A2** — contract & architecture only · `planes/` | ✅ Accepted |
| [0002](0002-core-repository-naming.md) | Core repository naming | **A** — `agent-platform` = contract owner · `agent-backend-os` = implementation | ✅ Accepted |
| [0003](0003-agent-gateway-boundary.md) | Agent gateway boundary | **A** — `agent-gateway` / `model-gateway` / `agent-fleet` | ✅ Accepted |
| [0004](0004-agent-vs-model-provider.md) | Agent vs model provider | **A** — Model Provider / Agent Provider / Agent Platform | ✅ Accepted |
| [0005](0005-agent-runtime-boundary.md) | Agent runtime boundary | **A + C2** — Workflow→Harness→Runtime→Sandbox · native + external ใต้ contract เดียว | ✅ Accepted |
| [0006](0006-contract-versioning.md) | Contract versioning | **A** versioning · **A2** ownership | ✅ versioning / ⏳ **ownership pending** |
| [0007](0007-multi-tenancy.md) | Multi-tenancy | **A** — Tenant → Workspace → Resource | ✅ Accepted |
| [0008](0008-reference-stack.md) | Reference stack | **A** — tech-neutral (YAML/JSON Schema) | ✅ Accepted |
| [0009](0009-capability-model.md) | Capability model | **A** — capability / declaration / requirement | ✅ Accepted |
| [0010](0010-risk-approval-taxonomy.md) | Risk & approval taxonomy | **A** — `action_risk` / `authority` / `severity` | ✅ Accepted |

การเคาะบันทึกไว้ที่ [issue #1–#10](https://github.com/monthop-gmail/agent-platform/issues?q=is%3Aissue+label%3Aadr) — **ไฟล์บันทึกว่าตัดสินอะไร issue บันทึกว่าใครตัดสินและเมื่อไหร่**

### ⏳ สิ่งเดียวที่ยังค้าง — ADR-0006 ownership

`agent-platform` **ยังไม่ใช่** canonical owner ของ shared contract จนกว่า Architecture Owner ของ [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) จะยืนยัน — RFC-0001–0004 ที่นั่นยัง `Draft` และ `GOVERNANCE.md` ระบุว่า owner ของ repo นั้นมีอำนาจสุดท้าย

ระหว่างรอ: contract ที่อ้าง RFC เหล่านั้น (`contracts/approval/` `contracts/event/` และ state machine) ติดสถานะ **`external-authority-pending`** ส่วน contract อื่นเดินได้ตามปกติ ดู [issue #6](https://github.com/monthop-gmail/agent-platform/issues/6)

## ศัพท์ที่ lock แล้ว

ห้ามใช้คำเหล่านี้ในเอกสารหรือ contract ใหม่:

| ห้ามใช้ | ใช้แทน | ที่มา |
| --- | --- | --- |
| `modules/` (ในความหมายที่เก็บ code) | `planes/` — Plane Boundary Documentation | 0001 |
| `enterprise-agent-backend` · `enterprise-agent-knowledge-platform` | `agent-backend-os` · `enterprise-knowledge` | 0002 |
| `gateway` เดี่ยว ๆ · `ai-agent-gateway` · `multi-agent-gateway` | `agent-gateway` / `model-gateway` / `agent-fleet` | 0003 |
| `LLM Adapter` · `Runtime Adapter` · `agent-adapters` · `AgentAdapter` · `agent-model-router` | Model Provider · Agent Provider | 0004 |
| `harness` ในความหมาย test rig | `evals` | 0005 |
| `Project` / `Department` เป็นชั้น id | label ของ workspace | 0007 |
| `risk_level` เดี่ยว ๆ | `action_risk` / `authority` / `severity` | 0010 |

## ลำดับที่เคาะไปแล้ว

```text
0001 (scope) ✅
  ↓
0002 (ชื่อ) ✅ ── 0004 (ศัพท์ provider) ✅
  ↓                ↓
0003 (gateway) ✅ ── 0005 (runtime) ✅ ── 0009 (capability) ✅   🔒 vocabulary gate — ผ่านแล้ว
  ↓
0006 (versioning ✅ / ownership ⏳) ── 0007 (tenancy) ✅ ── 0010 (risk/authority) ✅
  ↓
0008 (stack) ✅
  ↓
contracts/ P0  ← เริ่มได้แล้ว
```

## ที่มา

Context ในแต่ละ ADR ดึงจาก [`../ref/`](../ref/) (11 ไฟล์ raw) และจากการอ่าน repo จริง 3 ตัว — สรุปไว้ที่ [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) และ [`../ref/existing-repos.md`](../ref/existing-repos.md)
