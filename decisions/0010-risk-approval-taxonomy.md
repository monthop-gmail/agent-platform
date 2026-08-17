# ADR-0010: Risk & Approval Taxonomy

**Status:** Accepted (2026-08-17)
**Date:** 2026-08-17
**Depends on:** ADR-0009
**Blocking:** `contracts/policy/`, `contracts/approval/`, `contracts/capability/`

## Context

คำว่า `LOW / MEDIUM / HIGH / CRITICAL` ถูกใช้ใน 2 เอกสารด้วย **ความหมายที่ไม่ใช่เรื่องเดียวกัน** — ถ้าเอาไปใส่ contract โดยไม่แยก จะได้ field ที่อ่านได้สองแบบ

**[`backend-os §9`](../ref/enterprise-agent-backend-os-blueprint.md)** — แบ่งตาม **ชนิดของ action** (ความเสียหายถ้าทำผิด):

```text
LOW      read data · search · analyze
MEDIUM   create ticket · modify record
HIGH     payment · delete · production deploy · physical device command
```

**[`navi-security-agent` Phase 4](../ref/navi-security-agent-blueprint.md)** — แบ่งตาม **ระดับ automation ที่อนุญาต**:

```text
LOW       → AI automatic workflow
MEDIUM    → AI recommendation
HIGH      → Supervisor approval
CRITICAL  → Human command required
```

สองอันนี้ผูกกันแบบ *ผลลัพธ์* ไม่ใช่ *นิยาม* — action ที่เสี่ยงสูงควรต้องขออนุมัติมากขึ้น แต่ไม่ใช่ 1:1 เสมอ (เช่น `read data` ของข้อมูลชั้นความลับสูงเป็น action เสี่ยงต่ำแต่ต้องอนุมัติ)

มีมิติที่สามอีก — **[`navi-security-agent` §4/§8 (Risk Analyst)](../ref/navi-security-agent-blueprint.md)** ให้ agent ประเมิน `LOW/MEDIUM/HIGH/CRITICAL` ของ **สถานการณ์** (รถต้องสงสัยเข้าพื้นที่หวงห้าม) ซึ่งไม่ใช่ความเสี่ยงของ action และไม่ใช่ระดับ automation เลย

และ **[`backend-os §7`](../ref/enterprise-agent-backend-os-blueprint.md)** ใส่ `risk_level` + `approval_required` ไว้ใน tool schema — เป็นมิติที่ผูกกับ tool ไม่ใช่กับ request

## สาม concept ที่ต้องแยกชื่อ

| concept | ตอบคำถาม | ผูกกับ | ใครกำหนด |
| --- | --- | --- | --- |
| **Action Risk** | ทำผิดแล้วเสียหายแค่ไหน | tool / action / capability | คนออกแบบ tool (static) |
| **Authority Level** | ใครต้องอนุมัติก่อนทำ | policy decision | policy engine (runtime) |
| **Situation Severity** | สถานการณ์นี้ร้ายแรงแค่ไหน | domain event | agent ประเมิน (domain-specific) |

ทั้งสามมี 4 ระดับพอดีจึงถูกเผลอใช้คำเดียวกัน — แต่ค่าไม่ได้ map 1:1

## Options

### A. แยก 3 field คนละ enum (แนะนำ)

```yaml
# contracts/capability|tool
action_risk: low | medium | high | critical

# contracts/policy → ผลของ policy evaluation
authority: auto | notify | approval_required | human_command_only

# contracts/<domain> — domain-specific ไม่อยู่ใน contract กลาง
severity: (domain กำหนดเอง เช่น navi ใช้ low|medium|high|critical)
```

* ✅ `authority` ใช้คำที่บอกความหมายตัวเอง — อ่าน `approval_required` ไม่ต้องเดาว่า HIGH หมายถึงอะไร
* ✅ policy เขียน mapping ได้เองต่อ tenant: `action_risk: high` + `tenant: navi` → `authority: human_command_only` แต่ tenant อื่นอาจเป็น `approval_required`
* ✅ `severity` ออกจาก contract กลาง → `navi-security-agent` เก็บของตัวเองได้ ไม่ต้องบังคับ domain อื่นใช้
* ✅ ต่อกับ [ADR-0009](0009-capability-model.md) ได้ — capability ที่เสี่ยง (`shell`, `network_egress`, `autonomous_execution`) แปะ `action_risk` ตั้งแต่ taxonomy
* ❌ ต้องแก้ blueprint 2 ฉบับที่ใช้คำเดิม (เนื้อหาไม่เปลี่ยน แค่เปลี่ยนชื่อ field)

### B. ใช้ `risk_level` เดียว แล้วให้ policy ตีความ

* ✅ field เดียว เขียนง่าย
* ❌ ค่าเดียวกันหมายถึงคนละเรื่องในคนละ context — เป็นปัญหาที่ ADR นี้ตั้งใจแก้
* ❌ audit ย้อนหลังไม่รู้ว่า `HIGH` ที่บันทึกไว้คือ action เสี่ยงหรือสถานการณ์ร้ายแรง

### C. คงชื่อเดิมแต่ใส่ namespace (`risk.action` / `risk.authority` / `risk.severity`)

* ✅ ไม่ต้องเลิกใช้คำว่า risk
* ⚠️ ดีกว่า B แต่ยังชวนให้คนเทียบค่ากันข้าม namespace เพราะ enum เหมือนกัน — ถ้าเลือกทางนี้ต้องบังคับให้ enum ต่างกันด้วย

## ความสัมพันธ์กับ RFC-0002

`devfactory-core` RFC-0002 ให้ decision type `APPROVE / REJECT / REQUIRE_CHANGES` ซึ่งเป็น **ผลของการอนุมัติ** ไม่ใช่ระดับ authority — คนละ field กับ ADR นี้

```text
action_risk (static)
      ↓
policy evaluation → authority: approval_required
      ↓
approval request → RFC-0002 decision: APPROVE | REJECT | REQUIRE_CHANGES
```

ตรงกับที่ [extraction §2](../architecture/devfactory-core-rfc-extraction.md) สรุปว่า `contracts/policy/` กับ `contracts/approval/` ต้องแยกกัน

## Decision

**A** — แยกเป็น 3 field คนละ enum:

```yaml
action_risk: low | medium | high | critical                          # contracts/capability, contracts/tool
authority:   auto | notify | approval_required | human_command_only  # contracts/policy
severity:    (domain กำหนดเอง — ไม่อยู่ใน contract กลาง)
```

chain ที่ lock: `action_risk` → policy → `authority` → approval → decision (`APPROVE` / `REJECT` / `REQUIRE_CHANGES`)

**Reason:** ทั้งสามมี 4 ระดับพอดีจึงถูกเผลอใช้คำเดียวกัน แต่ค่าไม่ map 1:1 — `read data` ของข้อมูลชั้นความลับสูงเป็น action เสี่ยงต่ำแต่ต้องอนุมัติ · `authority` ใช้คำที่บอกความหมายตัวเองจึงอ่านแล้วไม่ต้องเดา และ policy เขียน mapping ต่อ tenant ได้เอง · `severity` ออกจาก contract กลางเพื่อไม่บังคับ domain อื่นใช้ enum ของงาน security · ปฏิเสธ B เพราะ audit ย้อนหลังจะแยกไม่ออกว่า `HIGH` คือ action เสี่ยงหรือสถานการณ์ร้ายแรง ปฏิเสธ C เพราะ enum เหมือนกันยังชวนให้เทียบค่าข้าม namespace

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

fallback บังคับเมื่อเจอค่าที่ไม่รู้จัก: `action_risk` → `critical` · `authority` → `human_command_only`

## Consequences ถ้าเลือก A

* `contracts/policy/` ต้องมีตาราง mapping `action_risk × tenant/profile → authority` เป็น config ไม่ใช่ hard-code
* `contracts/event/` บันทึกทั้ง `action_risk` และ `authority` ที่ใช้ตัดสิน — ไม่ใช่แค่ผลลัพธ์ (ต่อยอด backend-os §14 ที่มี `policy_result` เดี่ยว)
* fallback ที่ปลอดภัยเมื่อเจอค่าที่ไม่รู้จัก: `action_risk` → ถือเป็น `critical` · `authority` → ถือเป็น `human_command_only` (สอดคล้อง [ADR-0006](0006-contract-versioning.md) ที่บังคับ fallback ไปทาง deny/escalate)
* `navi-security-agent` เปลี่ยนคำในเอกสารตัวเอง: Phase 4 `LOW/MEDIUM/HIGH/CRITICAL` → `authority` · Risk Analyst `LOW/MEDIUM/HIGH/CRITICAL` → `severity`
* `backend-os §9` risk table → `action_risk` (ค่าเดิมใช้ได้ ไม่ต้องแก้เนื้อหา)

## Sources

[`../ref/enterprise-agent-backend-os-blueprint.md`](../ref/enterprise-agent-backend-os-blueprint.md) §7, §8, §9, §14 · [`../ref/navi-security-agent-blueprint.md`](../ref/navi-security-agent-blueprint.md) §4, §8, Phase 4 · [`../architecture/devfactory-core-rfc-extraction.md`](../architecture/devfactory-core-rfc-extraction.md) §2 · [`../ref/README.md`](../ref/README.md) ตารางข้อขัดแย้ง
