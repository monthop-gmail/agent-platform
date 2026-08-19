# Agent Platform — วิธีนำไปใช้กับ Repo ใหม่และ Repo เดิม

คู่มือสำหรับทีมที่จะเอา repo เข้า ecosystem — ไม่ใช่เอกสารอธิบายตัว platform

> **เอกสารนี้เป็นคำแนะนำ ไม่ใช่ authority** — ถ้าขัดกับ [`decisions/`](../decisions) หรือ [`contracts/`](../contracts) ให้ยึดสองที่นั้น และเปิด issue แจ้งว่าคู่มือผิด
>
> ที่มาที่ผูกพันจริง: [`contracts/README.md`](../contracts/README.md) · [`architecture/consumers.md`](../architecture/consumers.md) · [`planes/README.md`](../planes/README.md) · [ADR-0006](../decisions/0006-contract-versioning.md) · [ADR-0012](../decisions/0012-consent-contract.md)

---

## 1. วัตถุประสงค์

`agent-platform` คือ **Unified Agent Foundation** สำหรับใช้เป็นมาตรฐานกลางในการสร้าง เชื่อมต่อ ควบคุม ทดสอบ และ operate AI Agent หลายระบบ

```text
                    agent-platform
                          │
             ┌────────────┼────────────┐
             │            │            │
          Contract      Policy      Capability
             │            │            │
             └────────────┼────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
   Product Repo       Agent Repo        Harness Repo
       │                  │                  │
       ▼                  ▼                  ▼
     Odoo             Security           Coding
     Navi             Farm              Web
     IMS              Knowledge          Workflow
```

`agent-platform` **ไม่ใช่ implementation repository ของทุกระบบ** แต่เป็น:

* Architecture authority
* Contract authority
* Vocabulary authority
* Cross-agent interoperability layer
* Policy / capability boundary
* Conformance standard
* Ecosystem governance layer

Code จริงควรอยู่ใน repository ที่รับผิดชอบระบบนั้นโดยตรง ([ADR-0001](../decisions/0001-platform-scope.md))

---

## 2. Agent Platform เอาไปทำอะไรได้บ้าง

### 2.1 สร้าง AI Agent ใหม่

```text
Security Agent · Farm Agent · Knowledge Agent · Coding Agent
Workflow Agent · Care Agent · Operations Agent · Monitoring Agent · Customer Agent
```

Agent ไม่จำเป็นต้องใช้ model หรือ runtime vendor เดียวกัน

```text
OpenAI Agent · Claude Agent · Gemini Agent · Qwen Agent
DeepSeek Agent · Local Model Agent · Cloudflare Agent · Custom Runtime Agent
```

แต่ทุก agent พูดภาษากลางของ ecosystem ผ่าน contract ของ `agent-platform`

---

## 3. ใช้กับ Product/Application Repo

ตัวอย่าง: `navi-ims` · `odoo-farm` · enterprise application · IoT/VMS · ERP · CRM · Hospital system · Security system

Product ไม่จำเป็นต้องกลายเป็น AI Agent ทั้งระบบ — เพิ่ม AI capability เข้าไปได้:

```text
Application
    │
    ├── normal business logic
    │
    └── Agent Integration
            ├── capability
            ├── policy
            ├── tool
            ├── knowledge
            └── event
```

ตัวอย่าง `navi-ims`:

```text
Navi IMS
   ├── Incident
   ├── Camera
   ├── Patrol
   ├── Security
   │
   └── AI Agent
          ├── observe
          ├── analyze
          ├── recommend
          └── escalate
```

---

## 4. ใช้กับ Coding / DevFactory

`devfactory-core` ใช้ platform เป็นมาตรฐานกลางของ agent execution ecosystem

```text
User Request
     │
     ▼
DevFactory
     ├── Planner Agent
     ├── Coding Agent
     ├── Test Agent
     ├── Review Agent
     └── Release Agent
             │
             ▼
        GitHub Repo
```

`agent-platform` ไม่ต้องกลายเป็น coding engine แต่กำหนด contract กลางให้ agent ต่าง ๆ ทำงานร่วมกันได้ — **15 ตัวในปัจจุบัน**:

```text
identity · agent · capability · provider · model · tool · mcp
execution · policy · approval · consent · event · artifact · error · profile
```

รายการล่าสุดพร้อมสถานะอยู่ที่ [`contracts/README.md`](../contracts/README.md) — อย่าคัดลอกรายการนี้ไปใช้เป็นของจริง เพราะมันจะเก่า

---

## 5. ใช้กับ Multi-Agent System

```text
                 Agent Platform
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Planner          Specialist       Reviewer
       └───────────────┼────────────────┘
                       ▼
                    Executor
```

ตัวอย่าง:

```text
Security Agent
       ├── Vision Agent
       ├── Knowledge Agent
       ├── Policy Agent
       └── Notification Agent
```

แต่ละ agent เป็นคนละ repo และคนละ runtime ได้

---

## 6. ใช้กับ Knowledge / RAG

```text
                 Agent Platform
                       │
                 Knowledge Contract
                       ▼
             enterprise-knowledge
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Ingest        Index       Retrieval
                                      │
                                      ▼
                                  Agent
```

รองรับ: tenant · ACL · retrieval · citation · provenance · knowledge source · tool access · policy enforcement

RAG ไม่ควรเป็น isolated utility แต่เป็น capability ที่ agent อื่น consume ได้

---

## 7. ใช้กับ Workflow / Orchestration

```text
Request → Planner → Task A ──► Repo A
                     Task B ──► Repo B
                     Task C ──► Repo C
                        │
                     Review → Release
```

ใช้ `identity` `execution` `workflow` `event` `approval` `policy` `artifact` เป็นภาษากลาง

---

## 8. ใช้กับ Agent Gateway

```text
User / API / ChatGPT / App
             ▼
       Agent Gateway
      ┌──────┼──────┐
      ▼      ▼      ▼
    Agent  Agent  Agent
```

Gateway ดูแล: authentication · authorization · policy · quota · audit · routing · capability discovery

⚠️ คำว่า **gateway เดี่ยว ๆ ห้ามใช้** ตาม [ADR-0003](../decisions/0003-agent-gateway-boundary.md) — มีสามตัวที่คนละทิศทาง: `agent-gateway` (inbound) · `model-gateway` (outbound) · `agent-fleet` (fan-out)

---

## 9. ใช้กับ Vendor-native Agent

```text
                    Agent Platform
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
   OpenAI              Anthropic           Google
       ▼                  ▼                  ▼
    Agent              Agent              Agent
```

รวมถึง Claude Code · Gemini Code Assist · GitHub Copilot · Amazon Q · Qwen · DeepSeek · Local Agent · Custom Agent

> Vendor เป็น implementation/provider
> Agent Platform เป็น interoperability/governance layer

ดู [ADR-0004](../decisions/0004-agent-vs-model-provider.md) — **Model Provider ≠ Agent Provider**

---

## 10. ใช้กับ Repo ใหม่

เมื่อสร้าง repo ใหม่ **อย่าเริ่มด้วยการ copy code จาก agent-platform**

ให้เริ่มด้วยการกำหนดว่า repo ใหม่อยู่ตรงไหนของ ecosystem:

```text
New Repo
   ├── Product
   ├── Agent
   ├── Harness
   ├── Knowledge
   ├── Runtime
   ├── Gateway
   ├── Workflow
   └── Infrastructure
```

จากนั้นเลือก plane ที่ต้อง consume ([11 plane](../planes/README.md)) ตัวอย่าง Security Agent:

```text
navi-security-agent

consume:
- agent
- capability
- policy
- event
- execution
- tool
```

จากนั้นสร้าง `platform-contract.yaml` และทำ conformance test

---

## 11. Prompt มาตรฐานสำหรับ Repo ใหม่

```text
คุณกำลังสร้าง repository ใหม่ใน Agent Platform ecosystem

Repository:
<REPO_NAME>

Purpose:
<อธิบายระบบ>

Repository type:
<Product | Agent | Harness | Knowledge | Runtime | Gateway | Workflow | Infrastructure>

เป้าหมาย:
สร้างระบบนี้ให้สามารถทำงานร่วมกับ agent-platform โดยไม่สร้าง contract ที่ขัดกับ platform

ให้ดำเนินการดังนี้:

1. วิเคราะห์ว่า repository นี้ควรอยู่ใน ecosystem layer/plane ใด
2. ระบุ agent-platform contracts ที่ต้อง consume
3. ระบุ capability ที่ระบบ expose
4. ระบุ tools/MCP ที่ต้องใช้
5. ระบุ policy และ approval boundary
6. ระบุ execution model
7. ระบุ event ที่ต้อง publish/consume
8. ระบุ artifact ที่ต้องสร้าง
9. สร้าง platform-contract.yaml
10. เพิ่ม conformance test สำหรับ payload จริง
11. เพิ่ม release gate ให้ conformance test ผ่านก่อน release
12. ห้าม duplicate canonical contract จาก agent-platform
13. ถ้าต้องการ contract ใหม่ ให้เสนอผ่าน ADR/Issue ก่อน
14. แยก business semantics ของ repository ออกจาก platform wire contract
15. ตรวจสอบ compatibility กับ agent-platform ก่อน implementation

ผลลัพธ์ที่ต้องการ:

- architecture
- contract mapping
- platform-contract.yaml
- conformance tests
- implementation plan
- GitHub Issues
- dependency list
- risks
- open decisions

อย่า implement business logic ก่อน architecture และ contract mapping ผ่านการ review
```

---

## 12. Prompt สำหรับ Repo เดิม

Repo เดิมไม่ควรถูกบังคับให้ rewrite ใหม่ทั้งหมด

```text
Existing Repo → Inventory → Map to Agent Platform → Gap Analysis
              → Minimal Adapter → Conformance → Gradual Adoption
```

```text
นำ repository เดิมนี้เข้าสู่ Agent Platform ecosystem

Repository:
<REPO_NAME>

Repository URL:
<URL>

ห้าม rewrite ระบบเดิมโดยไม่จำเป็น

ให้ดำเนินการ:

1. วิเคราะห์ architecture ปัจจุบัน
2. วิเคราะห์ business semantics ที่ repository เป็นเจ้าของ
3. วิเคราะห์ API/event/tool/execution model ที่มีอยู่
4. map component ปัจจุบันเข้ากับ agent-platform planes
5. map contract ที่มีอยู่กับ agent-platform contracts
6. ระบุสิ่งที่ conform แล้ว
7. ระบุสิ่งที่ยังไม่ conform
8. ระบุสิ่งที่ควร adapter
9. ระบุสิ่งที่ควร refactor
10. ระบุสิ่งที่ไม่ควรแก้
11. สร้าง migration plan แบบ incremental
12. เพิ่ม platform-contract.yaml
13. เพิ่ม conformance test
14. เพิ่ม release gate
15. ห้ามย้าย business semantics มาเป็น ownership ของ agent-platform
16. หาก contract ใหม่จำเป็น ให้สร้าง GitHub Issue/ADR เพื่อขอ decision

เป้าหมายคือ:

Existing System + Agent Platform Contract = Platform-compatible Consumer

ไม่ใช่:

Existing System → Rewrite ใหม่ทั้งหมด
```

---

## 13. Prompt สำหรับ Repo เก่าที่มี AI Agent อยู่แล้ว

```text
ตรวจสอบ AI Agent ที่มีอยู่ใน repository นี้
และประเมินการนำเข้า Agent Platform

ให้วิเคราะห์:

- agent lifecycle
- model/provider
- tools
- MCP
- memory
- knowledge
- execution
- sandbox
- policy
- approval
- events
- observability
- artifacts
- errors

จากนั้น map เข้ากับ agent-platform planes:
gateway · runtime · harness · evals · tools · policy
knowledge · workflow · sandbox · observability · backend-os

อย่าสร้าง implementation ซ้ำกับของเดิมโดยไม่จำเป็น

ให้เสนอ:

A. Keep
B. Adapt
C. Refactor
D. Replace
E. Move to another repository

พร้อมเหตุผลและ migration sequence
```

---

## 14. Prompt สำหรับ Repo ที่ต้องทำงานร่วมหลาย Repo

กรณีสำคัญที่สุดของ ecosystem นี้คือหนึ่ง task อาจกระทบหลาย repository

```text
งานนี้เกี่ยวข้องกับหลาย repositories

Goal:
<GOAL>

Repositories:
- <REPO_A>
- <REPO_B>
- <REPO_C>

ให้ทำ cross-repository impact analysis

1. วิเคราะห์ dependency ระหว่าง repo
2. ระบุ owner ของแต่ละ decision
3. ระบุ contract ที่เกี่ยวข้อง
4. ระบุ event ที่ต้องส่งข้าม repo
5. ระบุ artifact ที่ต้องส่งต่อ
6. ระบุ repository ที่ต้องแก้ก่อน
7. ระบุ repository ที่รอ dependency
8. สร้าง execution graph
9. แบ่งงานเป็น GitHub Issues ต่อ repository
10. ระบุ acceptance criteria ของแต่ละ issue
11. ระบุ integration test ที่ต้องทำหลังทุก repo เสร็จ
12. ห้ามแก้ repository ที่ไม่มี authority โดยพลการ
13. หากมี conflict ให้หยุดและเสนอ decision/ADR

ผลลัพธ์:

Cross-Repo Plan
    ├── Repo A Issue
    ├── Repo B Issue
    ├── Repo C Issue
    └── Integration Verification

ระบุ dependency และ execution order ให้ชัดเจน
```

---

## 15. Prompt สำหรับ Agent Delivery Orchestrator

```text
คุณคือ Agent Delivery Orchestrator

หน้าที่ของคุณไม่ใช่ implement ทุกอย่างเอง

หน้าที่คือ:

User Intent → Understand → Decompose → Identify Repositories
→ Identify Owners → Create Delivery Plan → Dispatch Work
→ Monitor → Verify → Integrate → Report

สำหรับทุก request:

1. อ่าน context และ architecture
2. ระบุ affected repositories
3. ตรวจ agent-platform contracts
4. ตรวจ ownership
5. สร้าง execution graph
6. สร้าง GitHub Issues
7. ส่งงานไปยัง repo-specific agent
8. ติดตาม PR
9. ตรวจ CI/conformance
10. ตรวจ cross-repository compatibility
11. รัน integration verification
12. สรุปผลกลับผู้ร้องขอ

กฎสำคัญ:

- ห้ามให้ repo หนึ่งตัดสิน semantics ของ repo อื่น
- ห้ามสร้าง duplicate canonical contract
- ห้าม bypass policy/approval
- ห้ามถือว่า PR merge = system integration สำเร็จ
- ทุก cross-repo dependency ต้องมี traceability
- ทุก decision สำคัญต้องมี owner
```

---

## 16. Repo ใหม่ควรได้รับ Prompt แบบไหน

| ระดับ | Prompt |
| ----- | --------------------------------------- |
| L0 | `Analyze this repository` |
| L1 | `Map this repository to agent-platform` |
| L2 | `Make this repository conformant` |
| L3 | `Implement this platform capability` |
| L4 | `Deliver this cross-repository feature` |

**ไม่ควรเริ่มทุก repo ด้วย L3**

```text
Analyze → Map → Contract → Conformance → Implement → Deliver
```

---

## 17. Prompt สำหรับการวิเคราะห์ Repo อย่างเดียว

ใช้เมื่อยังไม่แน่ใจว่า repo ควรนำมาใช้หรือไม่:

```text
Analyze this repository against Agent Platform.

Do not modify code.

Determine:

1. What problem does this repo solve?
2. Is it Product, Agent, Harness, Knowledge, Runtime, Gateway, Workflow or Infrastructure?
3. Which agent-platform planes apply?
4. Which contracts apply?
5. What capabilities does it provide?
6. What dependencies does it have?
7. What should remain repository-owned?
8. What should be standardized through agent-platform?
9. What conflicts exist?
10. Should this repo consume agent-platform?
11. If yes, what is the minimum integration?

Return:

- Architecture Map
- Platform Mapping
- Contract Mapping
- Gap Analysis
- Recommendation
```

---

## 18. Prompt สำหรับสร้าง GitHub Issues

```text
Based on the approved Agent Platform mapping,
create implementation issues for this repository.

Each issue must contain:

- Objective
- Context
- Scope
- Files/components likely affected
- Agent Platform contract involved
- Dependencies
- Acceptance Criteria
- Conformance requirement
- Test requirement
- Out of Scope

Split issues so that each issue can be implemented and reviewed independently.

Do not create vague issues such as "integrate agent-platform".

Each issue must have a measurable Definition of Done.
```

---

## 19. Prompt สำหรับ Coding Agent

Coding Agent ไม่ควรได้รับ prompt ใหญ่ทั้งหมดของ ecosystem — ส่งเฉพาะ:

```text
Repository:
<repo>

Issue:
<issue>

Platform contracts:
<contracts>

Relevant architecture:
<architecture>

Dependencies:
<dependencies>

Acceptance Criteria:
<criteria>

Implement this issue only.

Rules:

- follow repository conventions
- follow pinned agent-platform contracts
- do not modify unrelated architecture
- do not create duplicate contracts
- add/update tests
- run conformance tests
- report files changed
- report tests executed
- report unresolved risks
```

---

## 20. Prompt สำหรับ Review Agent

```text
Review this pull request against:

1. Repository architecture
2. Agent Platform contracts
3. Pinned platform-contract.yaml
4. Security policy
5. Capability boundary
6. Event contract
7. Conformance tests
8. Backward compatibility
9. Cross-repository compatibility

Classify findings:

BLOCKER
HIGH
MEDIUM
LOW
NIT

Only request changes for actionable issues.

Do not redesign unrelated components.
```

---

## 21. หลักการสำคัญ: Platform ไม่ควรกลายเป็น Monorepo

ควรทำ:

```text
agent-platform
      ├── contract
      ├── architecture
      ├── policy
      ├── vocabulary
      └── conformance
             ▼
       Consumer Repos
```

ไม่ควรทำ:

```text
agent-platform
      ├── navi code
      ├── farm code
      ├── coding code
      ├── knowledge code
      ├── security code
      └── workflow code
```

> **Platform owns the contract. Consumer owns the implementation.**

ข้อยกเว้นเดียวที่มี code ใน repo นี้คือ [`conformance/`](../conformance/) ตาม [ADR-0011](../decisions/0011-conformance-automation.md) — ตรวจสอบอย่างเดียว ห้าม generate ห้ามแก้ไฟล์

---

## 22. วิธีตัดสินใจว่าอะไรควรอยู่ใน Agent Platform

### คำถามคัดกรองเบื้องต้น 5 ข้อ

| | คำถาม | ถ้าตอบ |
| --- | --- | --- |
| Q1 | หลาย repo ต้องใช้หรือไม่ | ใช่ → มีเหตุผลที่จะ standardize |
| Q2 | เป็น protocol/contract หรือ business logic | contract → platform · business logic → consumer |
| Q3 | ถ้าเปลี่ยนจะกระทบ ecosystem หรือไม่ | ใช่ → ต้องมี platform governance |
| Q4 | มี owner ชัดเจนหรือไม่ | ไม่มี → หยุดก่อน อย่า merge semantics เข้า platform |
| Q5 | implementation นี้เป็นของ repo ใด | ตอบได้ → implementation ควรอยู่ repo นั้น |

### เกณฑ์ที่ผูกพันจริงเมื่อจะขอ contract ใหม่ — ต้องครบทุกข้อ

ห้าคำถามข้างบนใช้คัดกรอง แต่**เกณฑ์ที่ตัดสินจริงคือ 4 ข้อใน [ADR-0012](../decisions/0012-consent-contract.md)** ซึ่งบันทึกไว้ที่ [`contracts/README.md`](../contracts/README.md):

| # | เกณฑ์ |
| --- | --- |
| 1 | มี contract ที่มีอยู่แล้วตอบคำถามนี้ได้หรือไม่ — **ถ้ามี ให้ขยายตัวนั้น** |
| 2 | จะมี consumer อย่างน้อย 2 ราย หรือมี 1 รายที่ใช้จริงแล้วและรายที่สองระบุตัวได้ |
| 3 | มี implementation จริงให้อ้าง ไม่ใช่ออกแบบจากจินตนาการ |
| 4 | platform เข้าใจ semantics พอที่จะเป็นผู้ตัดสินสุดท้าย หรือมีเจ้าของ semantics ที่ชัด |

คำขอที่ไม่ครบ 4 ข้อไม่ได้ถูกปฏิเสธถาวร — แต่ต้องรอให้ครบ ไม่ใช่ผ่านด้วยความน่าเชื่อของผู้ขอ

---

## 23. Definition of Done สำหรับ Consumer

```text
[ ] platform-contract.yaml
[ ] contract versions pinned
[ ] relevant planes identified
[ ] conformance tests
[ ] real payload validation
[ ] CI validation
[ ] release gate
[ ] owner identified
[ ] dependency documented
[ ] migration/compatibility documented
```

### สถานะ conformance

[ADR-0006](../decisions/0006-contract-versioning.md) นิยามไว้ **4 ค่า** — ใช้ค่าอื่นไม่ได้:

| ค่า | ความหมาย |
| --- | --- |
| `unknown` | ไม่มี manifest · ไม่เคยรัน · หรือ `last_verified` เกิน 90 วัน |
| `passing` | CI conformance ผ่าน และ `last_verified` ไม่เกิน 90 วัน |
| `failing` | test ไม่ผ่าน — **ห้ามปล่อย release** |
| `waived` | ยกเว้นชั่วคราว ต้องมีวันหมดอายุและ issue/ADR อ้างอิง |

เส้นทางปกติของ repo ใหม่:

```text
unknown ──(เพิ่ม manifest)──► unknown + declared
        ──(มี payload จริงให้ validate + CI)──► passing
```

⚠️ **`declared` ไม่ใช่สถานะ** — เป็นหมายเหตุใน [`architecture/consumers.md`](../architecture/consumers.md) ว่า repo ประกาศ pin แล้วแต่ยังไม่ผ่าน conformance · repo ที่ declared **ยังไม่ถือเป็น consumer** ตาม ADR-0006 แต่มีผลกับการตัดสินใจปิด contract version เพราะมีคนพึ่งพา v1 นั้นอยู่จริง

**`passing` ต้องพิสูจน์ด้วย payload จริง ไม่ใช่เพียงประกาศใน manifest** — ทั้งสอง consumer ที่ผ่านอยู่ตอนนี้รัน scenario จริงแล้ว validate event ที่ระบบผลิตออกมา ไม่ใช่ fixture ที่เขียนขึ้นเพื่อให้ schema ผ่าน

---

## 24. Architecture Flow ที่แนะนำสำหรับทั้ง Ecosystem

```text
                         USER
                           ▼
                Agent Delivery Orchestrator
                           ▼
                  Agent Platform
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
    Gateway             Workflow           Knowledge
       └───────────────────┼───────────────────┘
                  ┌────────┼────────┐
                  ▼        ▼        ▼
                Agent    Agent    Agent
                  ▼        ▼        ▼
                Repo A   Repo B   Repo C
                  └────────┼────────┘
                           ▼
                       GitHub
                  Issue / PR / CI
                           ▼
                     Verification
```

---

## 25. สรุปสำหรับทีม

Agent Platform ควรถูกมองว่าเป็น **Operating Contract ของ Agent Ecosystem** ไม่ใช่แค่ framework สำหรับสร้าง agent

| | ลำดับ |
| --- | --- |
| Repo ใหม่ | Define → Map → Contract → Conformance → Implement |
| Repo เดิม | Inventory → Map → Gap Analysis → Adapter → Conformance → Gradual Migration |
| งานหลาย repo | User Intent → Delivery Orchestrator → Cross-Repo Plan → Issues → Repo Agents → PRs → Conformance → Integration → Delivery |

กฎสูงสุด:

```text
Agent Platform = Common Language + Contract + Governance
Repository     = Implementation + Domain Semantics + Ownership
Orchestrator   = Coordination + Delegation + Verification
```

เมื่อมี repo ใหม่เข้ามา **ไม่ควรถามเพียงว่า "เอา agent-platform ไปติดตั้งอย่างไร"** แต่ควรถามว่า:

> **"Repo นี้มีบทบาทอะไรใน Agent Ecosystem และต้องใช้ contract/capability/plane ใดของ Agent Platform เพื่อทำงานร่วมกับ repo อื่นได้?"**

นี่จะทำให้ ecosystem ขยายจาก 5–10 repos ไปเป็นหลายสิบหรือหลายร้อย repos ได้ โดยไม่กลายเป็น architecture ที่ทุก repo เชื่อมกันเองแบบ point-to-point
