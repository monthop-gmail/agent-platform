ได้จร้า ผมมองเป็น **Companion Repo** ที่แยก lifecycle จาก `navi-ims` ชัดเจนเลย โดย `NAVI-IMS` เป็นระบบปฏิบัติการ/ข้อมูลกลาง ส่วน AI Agent เป็น “สมอง รปภ.” ที่เฝ้าดู วิเคราะห์ ประเมิน และช่วยตัดสินใจ

## ภาพรวม

![Image](https://images.openai.com/static-rsc-4/cAcAP7IO1wsDTLo3pzwcMbaC2_PMb4NkPainqsa9yI3OZOV84v03kems83o1F0QdFvbh1bwpJZOXECHOHeGUjzjMmwJUV_E7KCJ10zDWVVpKe3L6nBslY8CrKGD5V4a8mz90aQg8Q7Fk-_rCmGLwOqc83tAsPutCQFHUa3FOOjUSY0ipNdRQ6i_se1957jxY?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/Japa8nxzF3VYMwlpBovwV2sFvOSa3cA-4Hz5rudKrBeI29tttcn0-FnA7ASw8sn8Ny0FmnBD2gzcskHLc-zXoZVEtWy-2KBItXHIWZDzMAkBPDGhtCmE7dhGOOllMnPLyC-fEfudIEtbGgrSqTZ-Nbz-5YV-VcPBkPIcYOlMK8IbzEsDzfFd9DXhbuyEKv0_?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/bnJM1nSqHp2_55reM5rv-c5NJgMneqREyt4IbHsUNq2LvdXK6Oo1Xb_itZQREg3ooAMuLTIbsbUp9xSLR1CIjJGClRN7btV_I2LCcyz3Pa-0Dd9cHvPQDEF3JH6P32ssMEtX9vPWdmrSJQWQCKb46X7FJt53nW3uU_4t_nrQHAK5v0QNSJ524pGm_nlqe9eJ?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/hyMKQsfluwUgiuS0lNwT7sTwpC8t9BSSjau5Gok8w9sfuvQPxP7LSZ3rOca9yEJcguk-4LWGB9G2-qIEb7OMqezydMzU3PD1i9Ki83PXLbban-_3uA8nqZa1mNN5N_UO1_ToqCCJ5gU6DSQYt5yQzm63KOLaeB4Vw-SpWqbR5uEa5siZcI08AeId0MoLq0Ht?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/ePXotl6qPCa7fWR7LvThPkRNPjrfiF58fYG6-UZMSBYqv4gjaT9YA4eNG2P1e0G3Tb8ajAydebN7KkVUv_dsKvqcEu9lgFxvxuyVsUFfrux227Uyj-B8DNyrGkc34cOhbitel9tLvW5oXATJwcfu2I7hHi2U7PVegs9Qc6QNKFnGv7benPTs-fkCbhA-phX-?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/eLhTi_ol3rCIcwrLuHVl0YLnhnQuOMzGbyDpYg7mQ0I-xYPhA011kDh8acM0LUzN5BNxBScWHyX38wTaPEA1UEZ-X4-yU0AThTYeRVVNgXXTGbVzBc0dCDtWXMvpinu2GqmMzH_KGGPCOpaFtVMS2m8Dbm8-aJDwY9vjUJhzKI4xQGUHMPIY7klFCPgr7Xyr?purpose=fullsize)

```text
                         ┌──────────────────────────┐
                         │       NAVI-IMS           │
                         │      Odoo 19 Core        │
                         │                          │
                         │ Personnel / Mission      │
                         │ Incident / GPS           │
                         │ Camera / Sighting        │
                         │ Access / Geofence        │
                         │ Intelligence / Watchlist │
                         └────────────┬─────────────┘
                                      │
                         API / Events / Webhooks
                                      │
                                      ▼
                ┌────────────────────────────────────┐
                │       NAVI SECURITY AGENT           │
                │                                    │
                │  👁 Observer                       │
                │  🧠 Situation Analyst              │
                │  🚨 Risk Analyst                   │
                │  📋 Response Planner               │
                │  📡 Dispatcher                     │
                │  👮 AI Security Supervisor         │
                └────────────────┬───────────────────┘
                                 │
                ┌────────────────┼─────────────────┐
                ▼                ▼                 ▼
             Cameras          Sensors          Personnel
             Video/AI         GPS/IoT           Patrol
                │                │                 │
                └────────────────┼─────────────────┘
                                 ▼
                         Situation Awareness
                                 │
                         Risk / Decision
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
              Recommendation             Automation
                    │                         │
                    ▼                         ▼
              Human Operator             NAVI-IMS
```

ตัว `navi-ims` เองมีฐานที่เหมาะมากอยู่แล้ว ทั้ง Command Center, personnel, intelligence, geofence, access, geolocation, camera/video และ incident workflow

---

# 1. แบ่งหน้าที่ของสอง Repo

### `navi-ims`

**System of Record + Operations Platform**

รับผิดชอบ:

* บุคลากร
* หน่วย/กำลังพล
* ภารกิจ
* GPS
* กล้อง
* Access Control
* Geofence
* Sighting
* Watchlist
* Incident
* Command Center
* Workflow
* Notification
* Audit

### `navi-security-agent`

**AI Security Brain**

รับผิดชอบ:

* Observe
* วิเคราะห์เหตุการณ์
* รวมข้อมูลหลายแหล่ง
* Situation Awareness
* Risk Assessment
* Reasoning
* วางแผนตอบสนอง
* แนะนำกำลังพล
* สั่ง workflow ผ่าน policy
* ตรวจสอบผลลัพธ์
* เรียนรู้จาก incident
* Simulation / Evaluation

**ไม่ควร duplicate database หลักของ NAVI-IMS**

---

# 2. AI Agent ไม่ควรมีตัวเดียว

ผมแนะนำให้เริ่มจาก architecture แบบนี้:

```text
                    AI Security Supervisor
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
         Observer         Risk Analyst      Planner
             │                │                │
             ▼                ▼                ▼
          Events          Situation          Response
                           Context
                              │
                              ▼
                         Dispatcher
```

### Observer

เฝ้าดู event

```text
camera
GPS
SOS
geofence
access
sighting
sensor
incident
```

### Situation Analyst

เอา event หลายตัวมา correlate

เช่น

```text
Unknown Vehicle
+
Restricted Zone
+
กลางคืน
+
ไม่มี Access Request
+
เคยพบใกล้พื้นที่ 3 ครั้ง
```

กลายเป็น **สถานการณ์เดียว**

### Risk Analyst

ให้คะแนน:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

พร้อมเหตุผลและ evidence

### Response Planner

เสนอ:

```text
ตรวจกล้องเพิ่มเติม
ส่ง patrol
lockdown zone
แจ้ง supervisor
สร้าง incident
ติดตาม target
```

### Dispatcher

เป็นตัวเดียวที่สามารถเรียก tools/action ได้

แต่ต้องผ่าน:

```text
Policy
Authorization
Approval
Audit
```

---

# 3. หลักสำคัญ: AI ≠ Authority

ผมอยากให้ repo นี้มีแนวคิดนี้ตั้งแต่วันแรก:

```text
AI Recommendation
        ↓
Policy Engine
        ↓
Authorization
        ↓
Human Approval?
        ↓
Action
        ↓
Verification
        ↓
Audit
```

เช่น

```text
AI:
"พบรถต้องสงสัย"

       ↓

Risk:
HIGH

       ↓

Policy:
"High risk → แจ้ง supervisor"

       ↓

Supervisor:
Approve

       ↓

NAVI-IMS:
สร้าง Incident + ส่ง patrol
```

ส่วน action ที่มีผลกับระบบจริงควรมี permission boundary ชัดเจน

---

# 4. Event-driven Architecture

สอง repo ควรคุยกันผ่าน event/API มากกว่าผูก code กันโดยตรง

```text
NAVI-IMS
   │
   ├── sighting.created
   ├── incident.created
   ├── incident.updated
   ├── geofence.violation
   ├── access.requested
   ├── access.denied
   ├── patrol.sos
   ├── patrol.location.updated
   └── camera.alert
             │
             ▼
      Security Agent
             │
             ├── analyze
             ├── correlate
             ├── assess-risk
             └── plan-response
             │
             ▼
       agent.decision
             │
             ▼
          NAVI-IMS
```

ตรงนี้จะทำให้ในอนาคตเอา agent ไปต่อกับระบบอื่นได้ด้วย

---

# 5. Context / Memory

AI รปภ. ต้องรู้ **บริบท** ไม่ใช่แค่ event เดี่ยว

```text
Current Event
      +
Recent Events
      +
Location
      +
Personnel
      +
Mission
      +
Watchlist
      +
Historical Incidents
      +
Security Policies
      +
Camera Context
      ↓
Situation Context
```

แบ่ง memory เป็น:

### Short-term

เหตุการณ์ช่วงปัจจุบัน

### Episodic

เหตุการณ์ที่ผ่านมา

### Operational

ข้อมูลภารกิจ/พื้นที่/กำลังพล

### Policy

กฎความปลอดภัย

### Knowledge

SOP / คู่มือ / ระเบียบ

---

# 6. Harness ต้องเป็นส่วนหนึ่งของ Repo

อันนี้สำคัญมากสำหรับโปรเจกต์นี้

```text
harness/
├── scenarios/
│   ├── unknown-person.yaml
│   ├── watchlist-vehicle.yaml
│   ├── geofence-breach.yaml
│   ├── patrol-sos.yaml
│   └── multi-camera.yaml
│
├── expected/
├── replay/
├── evaluators/
└── reports/
```

เราจะสามารถทำ:

```text
Scenario
   ↓
จำลอง NAVI-IMS events
   ↓
AI Agent
   ↓
Decision
   ↓
Evaluator
   ↓
Score
```

แล้ววัดได้ว่า Agent รุ่นใหม่ **เก่งขึ้นหรือแย่ลง**

---

# 7. Roadmap

## Phase 0 — Foundation

**เป้าหมาย:** ทำให้สอง repo คุยกันได้

* [ ] สร้าง `navi-security-agent`
* [ ] NAVI-IMS API contract
* [ ] Event schema
* [ ] Authentication
* [ ] Agent configuration
* [ ] Docker Compose
* [ ] Local development
* [ ] Health check
* [ ] Audit log

---

## Phase 1 — AI Guard MVP

**เป้าหมาย:** มี รปภ. AI ตัวแรก

```text
Event
 ↓
Context
 ↓
LLM
 ↓
Risk
 ↓
Recommendation
```

ทำให้รองรับ:

* [ ] Incident analysis
* [ ] Sighting analysis
* [ ] Geofence violation
* [ ] SOS
* [ ] Watchlist match
* [ ] Risk scoring
* [ ] Explanation
* [ ] Evidence collection

**ยังไม่ autonomous action**

---

## Phase 2 — Multi-Agent

เพิ่ม:

* [ ] Observer Agent
* [ ] Analyst Agent
* [ ] Risk Agent
* [ ] Planner Agent
* [ ] Supervisor Agent
* [ ] Dispatcher Agent

มี Agent Supervisor เป็น orchestrator

```text
Event
 ↓
Supervisor
 ├─ Observer
 ├─ Analyst
 ├─ Risk
 └─ Planner
 ↓
Decision
```

---

## Phase 3 — Situation Awareness

อันนี้จะเริ่ม “ฉลาดจริง”

รวม:

```text
Camera
GPS
Access
Geofence
Sighting
Personnel
Mission
Historical incidents
```

แล้วสร้าง:

**Security Situation Graph**

เช่น

```text
Person A
   │
   ├── entered Zone B
   │
   ├── seen by Camera 03
   │
   ├── vehicle X
   │
   └── near Incident #102
```

---

## Phase 4 — AI Response

เริ่มจาก **Recommendation**

แล้วค่อยเป็น **Controlled Automation**

```text
LOW
 → AI automatic workflow

MEDIUM
 → AI recommendation

HIGH
 → Supervisor approval

CRITICAL
 → Human command required
```

---

## Phase 5 — Autonomous Security Operations

เมื่อระบบ stable แล้วค่อยไปถึง:

```text
24/7 AI Watch
      ↓
Detect
      ↓
Understand
      ↓
Assess
      ↓
Respond
      ↓
Verify
      ↓
Escalate
      ↓
Learn
```

เป้าหมายคือให้ AI เป็น **AI Security Operations Officer** ไม่ใช่ chatbot

---

# 8. Technology Stack ที่ผมแนะนำ

```text
navi-security-agent
│
├── Agent Runtime
├── FastAPI / Node API
├── Event Bus
├── Redis
├── PostgreSQL
├── Vector / Knowledge Store
├── Policy Engine
├── LLM Gateway
├── Tool Runtime
├── Harness
└── Evaluation
```

และทำ LLM ให้ **เปลี่ยน provider ได้**

```text
                 LLM Gateway
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
      OpenAI       Claude        Gemini
        │            │             │
        └────────────┼─────────────┘
                     ▼
                Agent Runtime
```

จะได้ไม่ lock-in

---

# 9. สิ่งที่ทีมควรทำเป็น Milestones

```text
M0  Repository & Architecture
M1  NAVI-IMS Connector
M2  Event Gateway
M3  AI Guard MVP
M4  Context & Memory
M5  Risk Engine
M6  Multi-Agent
M7  Situation Awareness
M8  Policy & Authorization
M9  Controlled Automation
M10 Harness & Evaluation
M11 Security Hardening
M12 Production Deployment
```

---

# 10. Definition of Done

สุดท้ายผมอยากให้ทีมทดสอบด้วยสถานการณ์จริง ไม่ใช่แค่ `pytest`

ตัวอย่าง:

```text
Scenario:
รถไม่รู้จักเข้าพื้นที่หวงห้ามเวลา 02:00

Expected:

✓ ตรวจพบ
✓ Correlate camera + access + geofence
✓ ระบุว่าเป็น vehicle เดียวกัน
✓ Risk = HIGH
✓ สร้าง incident
✓ แจ้ง supervisor
✓ แนะนำ patrol ที่เหมาะสม
✓ ไม่เปิดประตู/สั่ง physical action เอง
✓ ทุก decision มี evidence
✓ ทุก action มี audit trail
```

นี่จะทำให้ `navi-security-agent` กลายเป็น **AI Security Agent Platform** ที่ใช้กับ NAVI-IMS ได้ แต่อนาคตก็สามารถต่อกับระบบรักษาความปลอดภัยอื่นได้ด้วย

**สรุปสั้นที่สุด:**

> `navi-ims` = **ร่างกาย + ประสาทสัมผัส + Command Center**
> `navi-security-agent` = **สมอง + การวิเคราะห์ + การตัดสินใจ**
> `harness/evals` = **สนามฝึก + ห้องสอบ AI**
> `policy/authorization` = **กฎและอำนาจ**
> `event bus` = **ระบบประสาทที่เชื่อมทั้งหมด**

แนวนี้ผมว่าเหมาะมากที่จะให้ **Claude Code เป็นทีม implementation แล้วใช้ GitHub Issues/Milestones เป็น execution plan** ตาม workflow ที่เราทำกันอยู่ครับ
