# Consumer Pilot — `devfactory-core`

ทดสอบว่า `contracts/v1` ใช้กับ repo จริงได้ไหม โดยเอา [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) เป็นตัวนำร่อง

อ่านจาก clone ที่ commit `3b921ba` เมื่อ 2026-08-17

## 🔴 ข้อค้นพบแรก — ยังเป็น consumer ไม่ได้ตอนนี้

`devfactory-core` **ไม่มี code เลยแม้แต่บรรทัดเดียว** — `packages/*` ทั้ง 6 ตัวมีแค่ `README.md` บรรทัดเดียว (`# core module`) และ `apps/api-gateway/README.md` ก็เช่นกัน

ตาม [ADR-0006](../decisions/0006-contract-versioning.md) consumer ต้องมีครบ 3 ข้อ:

| ข้อกำหนด | สถานะ |
| --- | --- |
| `platform-contract.yaml` | ทำได้ทันที |
| conformance test ใน CI ที่ validate **payload จริง** | ❌ **ทำไม่ได้ — ไม่มี payload ให้ validate** |
| test เป็นเงื่อนไขของ release | ❌ ไม่มี release |

→ สถานะที่ถูกต้องคือ **`conformance.status: unknown`** ไม่ใช่ `passing` และตารางใน [`consumers.md`](consumers.md) ต้องสะท้อนตามนั้น

**แต่การนำร่องยังมีค่า** — สิ่งที่ทำได้คือ *contract alignment* ตรวจว่า RFC ที่มีอยู่กับ contract ของเราพูดเรื่องเดียวกันหรือเปล่า ซึ่งเจอของจริง 6 เรื่อง

---

## 1. Plane mapping

| `devfactory-core` | plane ของเรา | หมายเหตุ |
| --- | --- | --- |
| `packages/core` (state machine) | — | **job level** อยู่เหนือ `execution/v1` ไม่ตรงกับ plane ไหน |
| `packages/governance` | [`policy`](../planes/policy.md) + approval | RFC-0002 |
| `packages/orchestrator` | [`workflow`](../planes/workflow.md) | RFC-0004 |
| `packages/observability` | [`observability`](../planes/observability.md) | RFC-0003 |
| `packages/agents` | [`runtime`](../planes/runtime.md) | agent provider adapter |
| `packages/proxy` | ⚠️ **`model-gateway`** | ดู §2 |
| `apps/api-gateway` | ⚠️ ต้องถาม | ดู §2 |

## 2. ⚠️ ชื่อชนกัน 2 จุด

### `packages/proxy` = outbound provider access

`CONTRIBUTING.md` ระบุว่า Core ประกอบด้วย *"State machine · Governance engine · **Provider proxy** · Orchestration engine"*

"Provider proxy" คือการไปเรียก model provider ข้างนอก = **outbound** ซึ่งตาม [ADR-0003](../decisions/0003-agent-gateway-boundary.md) เราตั้งชื่อว่า **`model-gateway`**

ไม่ใช่ปัญหาทันที (คนละ repo คนละ scope) แต่ถ้าวันหนึ่ง `model-gateway` เกิดขึ้นจริง จะมีสองระบบทำเรื่องเดียวกัน — **ควรตกลงกันตั้งแต่ตอนนี้ว่า `devfactory-core/packages/proxy` เป็น implementation ภายในของ devfactory หรือจะยกไปเป็น `model-gateway` กลาง**

### `apps/api-gateway` — ยังไม่รู้ว่าทิศไหน

มีแค่ `# API Gateway` บรรทัดเดียว ตอบไม่ได้ว่าเป็น inbound (ตรงกับ `agent-gateway` ของเรา) หรือเป็นแค่ API ของ devfactory เอง

[ADR-0003](../decisions/0003-agent-gateway-boundary.md) ห้ามใช้คำว่า gateway เดี่ยว ๆ — **ต้องถามเจ้าของ repo ว่าหมายถึงตัวไหน** ก่อนที่จะมี code ลงไปแล้วแก้ยาก

---

## 3. State machine — RFC-0001 (job) ↔ `execution/v1`

สองอันนี้อยู่คนละระดับและ**ควรอยู่คนละระดับ** — RFC-0001 เขียนไว้เองว่า task-level state machine เป็น Future Work

| RFC-0001 (job) | `execution/v1` | ความสัมพันธ์ |
| --- | --- | --- |
| `DRAFT` | — | ยังไม่มี execution |
| `GOVERNANCE_ANALYSIS` | `authorizing` | คนละ granularity — job ประเมินครั้งเดียว execution ประเมินทุกครั้ง |
| `APPROVED` | — | gate ที่อนุญาตให้สร้าง execution ได้ |
| `REJECTED` | `rejected` | ⚠️ ดู §4.1 |
| `TASK_PLANNING` | — | job แตกเป็น execution หลายตัว |
| `IN_PROGRESS` | `queued` `running` | **1 job → N execution** |
| `VALIDATING` | `running` (execution ชนิด test) | |
| `DEPLOYABLE` | — | job level ล้วน |
| `COMPLETED` | `succeeded` | |
| `FAILED` | `failed` | ⚠️ ดู §4.2 |
| — | `cancelled` | ❌ RFC-0001 ไม่มี |
| — | `timed_out` | ❌ RFC-0001 ไม่มี |
| — | `awaiting_approval` | ❌ ดู §4.3 |

**ข้อสรุป: ไม่ขัดกัน แต่ไม่ครบ** — mapping ใช้ได้ ถ้ายอมรับว่าคนละชั้นและเติมช่องว่างข้างล่าง

---

## 4. ช่องว่างที่เจอ 6 เรื่อง

### 4.1 `REJECTED` มีความหมายต่างกัน

* RFC-0001: *"REJECTED can only return to DRAFT"* — กลับไปแก้แล้วยื่นใหม่ได้
* `execution/v1`: `rejected` เป็น **terminal** ต้องสร้าง execution ใหม่

ไม่ผิดทั้งคู่ เพราะ job แก้แล้วยื่นใหม่ได้ ส่วน execution ที่ถูกปฏิเสธไปแล้วไม่ควรฟื้น — แต่ **ต้องเขียนไว้ให้ชัด** ไม่งั้นคนอ่านสองเอกสารจะเข้าใจว่าขัดกัน

### 4.2 `FAILED` terminal ที่ job แต่ retry ได้ที่ execution

* RFC-0001: *"FAILED is terminal"*
* `execution/v1`: `failed → queued` ได้ถ้า `error.retryable` และ `attempt < max_attempts`

แปลว่า **retry เกิดที่ระดับ execution เท่านั้น** — job ที่ FAILED แล้วฟื้นไม่ได้ตาม RFC-0001

RFC-0001 เขียน Open Question ไว้เองว่า *"Retry semantics for FAILED"* — `execution/v1` ตอบให้แล้วแต่**เฉพาะระดับ execution** ระดับ job ยังไม่มีคำตอบ และเป็นของ `devfactory-core` ที่ต้องตัดสิน

### 4.3 mid-run approval ไม่มีที่แสดงในระดับ job

execution เข้า `awaiting_approval` กลางคันได้ (เช่น จะ merge PR) แต่ job ที่มี execution รออนุมัติอยู่ ยังเป็น `IN_PROGRESS` เฉย ๆ — **มองจาก job ไม่รู้ว่ากำลังรอคน**

เป็นช่องว่างของ RFC-0001 ไม่ใช่ของเรา

### 4.4 🔴 ไม่มี tenant ที่ไหนเลย

`devfactory-core` ไม่มีคำว่า tenant, workspace หรือ multi-tenancy ในเอกสารใดเลย — ออกแบบมาแบบ single-tenant โดยปริยาย

แต่ [ADR-0007](../decisions/0007-multi-tenancy.md) กำหนดว่า **`tenant_id` เป็น required ทุก contract ไม่มีข้อยกเว้น**

→ นี่คือช่องว่างที่ใหญ่ที่สุด และเป็นสิ่งที่ต้องแก้ที่ `devfactory-core` ไม่ใช่ที่ contract · ถ้าไม่แก้ devfactory จะ conform ไม่ผ่านตั้งแต่ field แรก

### 4.5 RFC-0003 `job_id` required — เข้ากันได้ทางเดียว

contract ของเราจะทำ `job_id` เป็น optional เพราะ event จาก `navi-ims` ไม่ได้เกิดจาก job

* devfactory → platform: **ปลอดภัย** (event ของ devfactory มี job_id เสมอ)
* platform → devfactory: **พัง** ถ้า devfactory บังคับ job_id แล้วเจอ event ที่ไม่มี

→ devfactory ต้องผ่อน `job_id` เป็น optional ตอนรับ event จากภายนอก

### 4.6 RFC-0002 ขาด field ที่ platform ต้องใช้

มี `decision` `reason` `timestamp` `authority` — ขาด `tenant_id` `execution_id` `expires_at` `action_risk` `policy_id` ตามที่ [extraction §2](devfactory-core-rfc-extraction.md) ระบุไว้

---

## 5. สิ่งที่ต้องทำเพื่อให้ `devfactory-core` เป็น consumer จริง

เรียงตามลำดับที่ปลดล็อกกัน:

| # | งาน | เจ้าของ | blocking |
| --- | --- | --- | --- |
| 1 | ตกลงเรื่อง authority ของ RFC-0001–0004 | Architecture Owner ของ devfactory-core | [issue #6](https://github.com/monthop-gmail/agent-platform/issues/6) · `approval/` `event/` |
| 2 | ตัดสินว่า `packages/proxy` และ `apps/api-gateway` คือ plane ไหน | devfactory-core | ชื่อชนกันในอนาคต |
| 3 | เพิ่ม `tenant_id` เข้า job/decision/event model | devfactory-core | §4.4 — ต้องมี RFC ใหม่ตาม `CONTRIBUTING.md` |
| 4 | เติม `cancelled` / `timed_out` และตอบเรื่อง job-level retry | devfactory-core | §4.2 §4.3 |
| 5 | เขียน code ที่ผลิต payload จริง | devfactory-core | conformance test |
| 6 | เพิ่ม `platform-contract.yaml` + conformance CI | devfactory-core | ขึ้นทะเบียน consumer |

**ข้อ 3 ต้องมี RFC ใหม่** — `CONTRIBUTING.md` ของ repo นั้นระบุว่า *"Architecture changes require an RFC before implementation"* และ multi-tenancy เป็น architecture change แน่นอน

---

## 6. contract ที่ `devfactory-core` จะ pin (เมื่อพร้อม)

จาก `MILESTONE_v0.1.md` (job state machine · governance decision · audit log · e2e simulation):

```yaml
contracts:
  - identity/v1      # tenant/workspace/principal — §4.4 ต้องแก้ก่อน
  - execution/v1     # ผูกกับ job state machine ระดับบน
  - policy/v1        # governance decision interface
  - error/v1
  # - approval/v1    ⏸ external authority
  # - event/v1       ⏸ external authority
```

ร่าง manifest เตรียมไว้ที่ `/opt/docker-test/devfactory-core/platform-contract.yaml` (**ยังไม่ push** — ต้องให้เจ้าของ repo เห็นชอบก่อนตาม `CONTRIBUTING.md`)

---

## 7. สรุปสำหรับ platform

**contract v1 ไม่ต้องแก้จากการนำร่องครั้งนี้** — ทุกช่องว่างที่เจออยู่ฝั่ง `devfactory-core` ไม่ใช่ฝั่ง contract

สิ่งที่ยืนยันได้:

* การแยก job / execution / step เป็น 3 ชั้น **ถูกต้อง** — RFC-0001 เขียนเองว่า task-level เป็น Future Work และช่องนั้นว่างพอดี
* `execution/v1` ครอบสิ่งที่ RFC-0001 ไม่มี (`cancelled` `timed_out` `awaiting_approval` retry) โดยไม่ทับของเดิม
* ⚠️ แต่ **ยังไม่ได้พิสูจน์ด้วย payload จริง** เพราะ devfactory ไม่มี code — การนำร่องนี้เป็น *document alignment* ไม่ใช่ *conformance*

ถ้าอยากได้ conformance จริง ต้องหา consumer ที่มี code อยู่แล้ว — ตัวเดียวที่เข้าข่ายคือ [`navi-ims`](https://github.com/monthop-gmail/navi-ims) ซึ่งมี controller และ payload จริง แต่เป็น system of record ไม่ใช่ agent consumer โดยตรง
