# Existing repos (ใช้เป็น ref)

repo 2 ตัวนี้มีอยู่ก่อนแล้ว — **ไม่ต้องเขียน blueprint ใหม่** ให้ใช้ของจริงเป็น reference

สำรวจจาก remote เมื่อ 2026-08-17 (ยังไม่ได้อ่าน source ละเอียด แค่ inventory โครงสร้าง)

---

## `devfactory-core`

<https://github.com/monthop-gmail/devfactory-core>

> Governance-first AI infrastructure for autonomous DevOps and multi-agent orchestration.

* public · default branch **`main`** · push ล่าสุด 2026-02-18

```text
devfactory-core/
├── ARCHITECTURE.md
├── GOVERNANCE.md
├── CONTRIBUTING.md · CODE_OF_CONDUCT.md
├── apps/
│   └── api-gateway/
├── packages/
│   ├── core/            (+ state-machine.md)
│   ├── orchestrator/
│   ├── agents/
│   ├── governance/
│   ├── observability/
│   └── proxy/
├── docs/
│   ├── governance/
│   │   ├── CORE_BOUNDARY.md
│   │   ├── MILESTONE_v0.1.md
│   │   └── README_NORTH_STAR.md
│   ├── roadmap.md
│   └── issue-triage.md
├── rfcs/
│   ├── 0001-job-state-machine.md
│   ├── 0002-governance-decision-contract.md
│   ├── 0003-audit-event-log-schema.md
│   └── 0004-orchestration-execution-boundary.md
└── references/
    └── chatgpt-chats/
```

### ตอบช่องว่างที่เคยลิสต์ไว้ได้เลย

| ช่องว่าง | ของจริงอยู่ที่ |
| --- | --- |
| Audit / observability event schema | `rfcs/0003-audit-event-log-schema.md` |
| Policy / decision contract | `rfcs/0002-governance-decision-contract.md` |
| ขอบเขต core vs product | `docs/governance/CORE_BOUNDARY.md` |
| Job / task state machine | `rfcs/0001` + `packages/core/state-machine.md` |
| เส้นแบ่ง orchestration vs execution | `rfcs/0004-orchestration-execution-boundary.md` |

**ข้อควรระวัง:** repo นี้มี `apps/api-gateway/` และ `packages/governance` `packages/observability` `packages/orchestrator` อยู่แล้ว — ทับกับ `agent-gateway` / `policy-engine` / `observability` / `workflow` ใน blueprint ฝั่ง platform ต้องเคาะเส้นแบ่งก่อนเริ่มเขียน code

---

## `navi-ims`

<https://github.com/monthop-gmail/navi-ims>

> Patrol Command Center — Odoo 19 + Inngest + Celery + Bull + MediaMTX

* public · default branch **`master`** (ไม่ใช่ `main`) · Python · push ล่าสุด 2026-03-22

```text
navi-ims/
├── docker-compose.yml
├── odoo/addons/
│   ├── patrol_command/         Command Center, GPS, notification, external API
│   ├── patrol_access/          access control + sighting
│   ├── patrol_geofence/
│   ├── patrol_geolocation/
│   ├── patrol_intelligence/    watchlist / intel
│   ├── patrol_personnel/
│   └── patrol_inventory/
├── celery-worker/
├── inngest-worker/
├── node-service/
├── mediamtx/                   video / RTSP
└── docs/
    ├── flows/
    │   ├── ai-detection.md
    │   ├── sos-incident.md
    │   ├── mission-lifecycle.md
    │   ├── access-control.md
    │   ├── maintenance.md
    │   └── supply-request.md
    ├── PRESENTATION.md
    └── TESTING.md
```

### API surface ที่มีอยู่จริง (controllers)

ใช้เป็นฐานของ NAVI-IMS API contract ที่ `navi-security-agent` Phase 0 ต้องการ

```text
patrol_command/controllers/
├── external_api.py         ← จุดเชื่อมภายนอก
├── command_center.py
├── dashboard_api.py
├── gps_server.py
└── notification_api.py

patrol_access/controllers/
├── access_api.py
└── sighting_api.py

patrol_geofence/controllers/geofence_check.py
patrol_geolocation/controllers/geolocation_api.py
```

`docs/flows/*.md` 6 ไฟล์ map ตรงกับ event ที่ blueprint ของ agent ต้องใช้ (sos, access, ai-detection, mission)

**ข้อควรระวัง:** blueprint ของ `navi-security-agent` สมมติว่ามี event bus + event schema 9 ตัว แต่ของจริงตอนนี้เป็น **HTTP controllers + Inngest/Celery worker** — ต้องเช็คก่อนว่า event ที่ต้องการมีอยู่แล้ว หรือต้องเพิ่มฝั่ง navi-ims

---

## `ai-web-harness`

<https://github.com/monthop-gmail/ai-web-harness>

> PoC: Harness that enforces a web-build workflow (requirement → design → implement → test → review → fix) while leaving room for model creativity. Themes: swiss / brutalist / editorial / japanese / playful.

* public · default branch `main` · Astro · MIT · push ล่าสุด 2026-08-14

```text
ai-web-harness/
├── CLAUDE.md
├── docs/architecture.md
├── harness/
│   ├── checks/          (ยังว่าง)
│   └── workflow/        (ยังว่าง)
├── skills/
│   ├── frontend/ · visual-qa/ · web-design/   (ยังว่าง)
├── themes/
│   └── swiss/ brutalist/ editorial/ japanese/ playful/   (ยังว่าง)
├── tests/
│   ├── functional/ · visual/   (ยังว่าง)
├── app/
│   └── pages/index.astro
├── ref/
│   ├── 2026-08-14-ai-web-harness-plan-raw.md
│   └── 2026-08-14-claude-code-prompt-milestones-raw.md
├── docker-compose.yml · Dockerfile · nginx.conf
└── astro.config.mjs
```

**สถานะจริง:** ยังเป็น scaffold — โครง directory ครบแต่ส่วนใหญ่เป็น `.gitkeep` ของที่มีเนื้อจริงคือ `CLAUDE.md`, `docs/architecture.md`, `README.md`, `app/pages/index.astro` และ raw docs ใน `ref/`

### สิ่งที่ใช้ได้เลย

* **แพตเทิร์น `ref/` แบบมี date prefix** — `YYYY-MM-DD-<topic>-raw.md` ควรเอามาใช้กับ `ref/` ของ repo นี้ด้วย จะได้เรียงตามเวลาและรู้ว่าอันไหน raw
* `harness/workflow` + `harness/checks` = โครงของ execution policy ที่ blueprint อื่นเรียกว่า harness
* `skills/` = แพตเทิร์นเดียวกับ Claude Code skills

**ข้อควรระวัง:** repo นี้เป็น harness **เฉพาะงาน web build** ไม่ใช่ `agent-harness` กลางตามไฟล์ naming convention — blueprint ฝั่ง OAuth gateway §17 ก็ระบุชัดว่า `ai-web-harness` ทำ orchestration/workflow ส่วน gateway ทำ auth/routing คนละชั้นกัน

---

## สรุปสถานะ ref หลังเพิ่มไฟล์นี้

| Core repo | ref |
| --- | --- |
| `agent-backend-os` | ✅ blueprint |
| `agent-gateway` | ⚠️ ยังไม่มีของตัวเอง (inbound/outbound ชื่อชนกัน) |
| `agent-harness` | ⚠️ ยังไม่มีตัวกลาง — มี `ai-web-harness` (web เท่านั้น) + adapter framework ใน blueprint distributed gateway |
| `enterprise-knowledge` | ✅ blueprint |
| `devfactory-core` | ✅ ของจริง (ไฟล์นี้) |
| `navi-ims` | ✅ ของจริง (ไฟล์นี้) |
| `navi-security-agent` | ✅ blueprint |

repo ที่มีอยู่จริงแล้ว 3 ตัว: `devfactory-core` · `navi-ims` · `ai-web-harness`
